# Copyright 2022 The Luxenstudio Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# From https://github.com/ashawkey/stable-dreamfusion/blob/main/luxen/sd.py

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F
from diffusers import PNDMScheduler, StableDiffusionPipeline
from rich.console import Console
from torch import nn
from transformers import logging

CONSOLE = Console(width=120)
logging.set_verbosity_error()
IMG_DIM = 512
const_scale = 0.18215


class StableDiffusion(nn.Module):
    """Stable Diffusion implementation"""

    def __init__(self, device) -> None:
        super().__init__()

        self.device = device

        try:
            with open("./HF_TOKEN", "r") as f:
                self.token = f.read().replace("\n", "")
                CONSOLE.print(f"Hugging face access token loaded.")
        except FileNotFoundError as e:
            raise AssertionError(
                f"Cannot read hugging face token, make sure to save your Hugging Face token at `./HF_TOKEN`"
            )

        SD_SOURCE = "stabilityai/stable-diffusion-2-1"
        CLIP_SOURCE = "openai/clip-vit-large-patch14"

        self.num_train_timesteps = 1000
        self.min_step = int(self.num_train_timesteps * 0.02)
        self.max_step = int(self.num_train_timesteps * 0.98)

        self.scheduler = PNDMScheduler(
            beta_start=0.00085,
            beta_end=0.012,
            beta_schedule="scaled_linear",
            num_train_timesteps=self.num_train_timesteps,
        )
        self.alphas = self.scheduler.alphas_cumprod.to(self.device)

        pipe = StableDiffusionPipeline.from_pretrained(SD_SOURCE, torch_dtype=torch.float16)
        pipe = pipe.to(self.device)

        # MEMORY IMPROVEMENTS
        pipe.enable_attention_slicing()

        # Needs xformers package (installation is from source https://github.com/facebookresearch/xformers)
        # pipe.enable_xformers_memory_efficient_attention()

        # More memory savings for 1/3rd performance
        # pipe.enable_sequential_cpu_offload()

        self.tokenizer = pipe.tokenizer
        self.unet = pipe.unet
        self.text_encoder = pipe.text_encoder
        self.auto_encoder = pipe.vae

        self.unet.to(memory_format=torch.channels_last)

        CONSOLE.print(f"Stable Diffusion loaded!")

    def get_text_embeds(self, prompt, negative_prompt):
        # prompt, negative_prompt: [str]

        # Tokenize text and get embeddings
        text_input = self.tokenizer(
            prompt,
            padding="max_length",
            max_length=self.tokenizer.model_max_length,
            truncation=True,
            return_tensors="pt",
        )

        with torch.no_grad():
            text_embeddings = self.text_encoder(text_input.input_ids.to(self.device))[0]

        # Do the same for unconditional embeddings
        uncond_input = self.tokenizer(
            negative_prompt, padding="max_length", max_length=self.tokenizer.model_max_length, return_tensors="pt"
        )

        with torch.no_grad():
            uncond_embeddings = self.text_encoder(uncond_input.input_ids.to(self.device))[0]

        # Cat for final embeddings
        text_embeddings = torch.cat([uncond_embeddings, text_embeddings])
        return text_embeddings

    def sds_loss(self, text_embeddings, luxen_output, guidance_scale=100):
        luxen_output_np = luxen_output.squeeze(0).permute(1, 2, 0).detach().cpu().numpy()
        luxen_output_np = np.clip(luxen_output_np, 0.0, 1.0)
        plt.imsave("luxen_output.png", luxen_output_np)
        luxen_output = F.interpolate(luxen_output, (IMG_DIM, IMG_DIM), mode="bilinear")
        t = torch.randint(self.min_step, self.max_step + 1, [1], dtype=torch.long, device=self.device)
        latents = self.imgs_to_latent(luxen_output)
        # predict the noise residual with unet, NO grad!
        with torch.no_grad():
            # add noise
            noise = torch.randn_like(latents)
            latents_noisy = self.scheduler.add_noise(latents, noise, t)
            # pred noise
            latent_model_input = torch.cat([latents_noisy] * 2)
            noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=text_embeddings).sample

        # perform guidance (high scale from paper!)
        noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
        noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
        # with torch.no_grad():
        #     diffused_img = self.latents_to_img(latents_noisy - noise_pred)
        #     diffused_img = diffused_img.detach().cpu().permute(0, 2, 3, 1).numpy().reshape((512, 512, 3))
        #     diffused_img = (diffused_img * 255).round().astype("uint8")
        #     plt.imsave("sdimg.png", diffused_img)

        # w(t), sigma_t^2
        w = 1 - self.alphas[t]
        # w = self.alphas[t] ** 0.5 * (1 - self.alphas[t])
        grad = w * (noise_pred - noise)

        # clip grad for stable training?
        # grad = grad.clamp(-10, 10)
        grad = torch.nan_to_num(grad)

        # noise_difference = self.latents_to_img(grad)
        # plt.imsave('noise_difference.png', noise_difference.view(3, 512, 512).permute(1, 2, 0).detach().cpu().numpy())

        # manually backward, since we omitted an item in grad and cannot simply autodiff.
        # _t = time.time()

        noise_loss = torch.mean(torch.nan_to_num(torch.square(noise_pred - noise)))

        # print('SDS LOSS:', noise_loss)

        return noise_loss, latents, grad

    def produce_latents(
        self, text_embeddings, height=IMG_DIM, width=IMG_DIM, num_inference_steps=50, guidance_scale=7.5, latents=None
    ):

        if latents is None:
            latents = torch.randn(
                (text_embeddings.shape[0] // 2, self.unet.in_channels, height // 8, width // 8), device=self.device
            )

        self.scheduler.set_timesteps(num_inference_steps)

        with torch.autocast("cuda"):
            for t in self.scheduler.timesteps:
                # expand the latents if we are doing classifier-free guidance to avoid doing two forward passes.
                latent_model_input = torch.cat([latents] * 2)

                # predict the noise residual
                with torch.no_grad():
                    noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=text_embeddings)["sample"]

                # perform guidance
                noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)

                # compute the previous noisy sample x_t -> x_t-1
                latents = self.scheduler.step(noise_pred, t, latents)["prev_sample"]

        return latents

    def latents_to_img(self, latents):

        latents = 1 / const_scale * latents

        with torch.no_grad():
            imgs = self.auto_encoder.decode(latents).sample

        imgs = (imgs / 2 + 0.5).clamp(0, 1)

        return imgs

    def imgs_to_latent(self, imgs):
        # imgs: [B, 3, H, W]
        imgs = 2 * imgs - 1

        posterior = self.auto_encoder.encode(imgs).latent_dist
        latents = posterior.sample() * const_scale

        return latents

    def prompt_to_img(self, prompts, negative_prompts="", num_inference_steps=50, guidance_scale=7.5, latents=None):

        prompts = [prompts] if isinstance(prompts, str) else prompts
        negative_prompts = [negative_prompts] if isinstance(negative_prompts, str) else negative_prompts
        text_embeddings = self.get_text_embeds(prompts, negative_prompts)
        latents = self.produce_latents(
            text_embeddings,
            height=IMG_DIM,
            width=IMG_DIM,
            latents=latents,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
        )  # [1, 4, resolution, resolution]

        diffused_img = self.latents_to_img(latents)
        diffused_img = diffused_img.detach().cpu().permute(0, 2, 3, 1).numpy()
        diffused_img = (diffused_img * 255).round().astype("uint8")

        return diffused_img


def seed_everything(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", type=str)
    parser.add_argument("--negative", default="", type=str)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--steps", type=int, default=50)
    opt = parser.parse_args()

    seed_everything(opt.seed)

    device = torch.device("cuda")

    with torch.no_grad():

        sd = StableDiffusion(device)

        imgs = sd.prompt_to_img(opt.prompt, opt.negative, opt.steps)

        plt.imsave("test_sd.png", imgs[0])
