# Blender VFX add-on

<p align="center">
    <iframe width="728" height="409" src="https://www.youtube.com/embed/vDhj6j7kfWM" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</p>

## Overview

This Blender add-on allows for compositing with a Luxenstudio render as a background layer by generating a camera path JSON file from the Blender camera path, as well as a way to import Luxenstudio JSON files as a Blender camera baked with the Luxenstudio camera path. This add-on also allows compositing multiple Luxen objects into a Luxen scene. This is achieved by importing a mesh or point-cloud representation of the Luxen scene from Luxenstudio into Blender and getting the camera coordinates relative to the transformations of the Luxen representation. Dynamic FOV from the Blender camera is supported and will match the Luxenstudio render. Perspective, equirectangular, VR180, and omnidirectional stereo (VR 360) cameras are supported. This add-on also supports Gaussian Splatting scenes as well, however equirectangular and VR video rendering is not currently supported for splats.

<center>
 <img width="800" alt="image" src="https://user-images.githubusercontent.com/9502341/211442247-99d1ebc7-3ef9-46f7-9bcc-0e18553f19b7.PNG">
</center>

## Add-on Setup Instructions

1. The add-on requires Blender 3.0 or newer, install Blender [here](https://www.blender.org/).

2. Download <a href="https://raw.githubusercontent.com/luxenstudio-project/luxenstudio/main/luxenstudio/scripts/blender/luxenstudio_blender.py" download="luxenstudio_blender.py">Blender Add-on Script</a>

3. Install and enable the add-on in Blender in `Edit → Preferences → Add-Ons`. The add-on will be visible in the Render Properties tab on the right panel.
    <center>
   <img width="500" alt="image" src="https://user-images.githubusercontent.com/9502341/232202430-d4a38ac7-2566-4975-97a4-76220f336511.png">
   </center>

4. The add-on should now be installed in the `Render Properties` panel
    <center>
   <img width="300" alt="image" src="https://user-images.githubusercontent.com/9502341/232202091-c13c66c4-f119-4f15-aa3e-3bf736371821.png">
   </center>

## Scene Setup

1. Export the mesh or point cloud representation of the Luxen from Luxenstudio, which will be used as reference for the actual Luxen in the Blender scene. Mesh export at a good quality is preferred, however, if the export is not clear or the Luxen is large, a detailed point cloud export will also work. Keep the `save_world_frame` flag as False or in the viewer, de-select the "Save in world frame" checkbox to keep the correct coordinate system for the add-on.

2. Import the mesh or point cloud representation of the Luxen into the scene. You may need to crop the mesh further. Since it is used as a reference and won't be visible in the final render, only the parts that the blender animation will interact with may be necessary to import.

3. Select the Luxen mesh or point cloud in the add-on.

4. Resize, position, or rotate the Luxen representation to fit your scene.

## Generate Luxenstudio JSON Camera Path from Blender Camera

1. There are a few ways to hide the reference mesh for the Blender render

   - In object properties, select "Shadow Catcher". This makes the representation invisible in the render, but all shadows cast on it will render. You may have to switch to the cycles renderer to see the shadow catcher option.
   <center>
   <img width="300" alt="image" src="https://user-images.githubusercontent.com/9502341/211244787-859ca9b5-6ba2-4056-aaf2-c89fc6370c2a.png">
   </center>

   - Note: This may not give ideal results if the mesh is not very clear or occludes other objects in the scene. If this is the case, you can hide the mesh from the render instead by clicking the camera button in the Outliner next to its name.
   <center>
   <img width="300" alt="image" src="https://user-images.githubusercontent.com/9502341/211244858-54091d36-086d-4211-a7d9-75dcfdcb1436.png">
   </center>

2. Verify that the animation plays and the Luxen representation does not occlude the camera.
3. Go to the Luxenstudio Add-on in Render Properties and expand the "Luxenstudio Path Generator" tab in the panel. Use the object selector to select the Luxen representation. Then, select the file path for the output JSON camera path file.
4. Click "Generate JSON file". The output JSON file is named `camera_path_blender.json`.
<center>
<img width="800" alt="image" src="https://user-images.githubusercontent.com/9502341/211442361-999fe040-a1ed-43f0-b079-0c659d70862f.png">
</center>

5. Render the Luxen with the generated camera path using Luxenstudio in the command prompt or terminal.

6. Before rendering the Blender animation, go to the Render Properties and in the Film settings select "Transparent" so that the render will be rendered with a clear background to allow it to be composited over the Luxen render.
<center>
<img width="200" alt="image" src="https://user-images.githubusercontent.com/9502341/211244801-c555c3b5-ab3f-4d84-9f64-68559b03ff37.png">
</center>

7. Now the scene can be rendered and composited over the camera aligned Luxenstudio render.
<center>
<img width="800" alt="image" src="https://user-images.githubusercontent.com/9502341/211245025-2ef5adbe-9306-4eab-b761-c78e3ec187bd.png">
</center>

### Examples

<p align="center">
    <img width="300" alt="image" src="https://user-images.githubusercontent.com/9502341/212463397-ba34d60f-a744-47a1-95ce-da6945a7fc00.gif">
    <img width="300" alt="image" src="https://user-images.githubusercontent.com/9502341/212461881-e2096710-4732-4f20-9ba7-1aeb0d0d653b.gif">
</p>

### Additional details

- You can also apply an environment texture to the Blender scene by using Luxenstudio to render an equirectangular image (360 image) of the Luxen from a place in the scene.
- The settings for the Blender equirectangular camera are: "Panoramic" camera type and panorama type of "Equirectangular".
    <center>
    <img width="200" alt="image" src="https://user-images.githubusercontent.com/9502341/211245895-76dfb65d-ed81-4c36-984a-4c683fc0e1b4.png">
    </center>

- The generated JSON camera path follows the user specified frame start, end, and step fields in the Output Properties in Blender. The JSON file specifies the user specified x and y render resolutions at the given % in the Output Properties.
- The add-on computes the camera coordinates based on the active camera in the scene.
- FOV animated changes of the camera will be matched with the Luxen render.
- Perspective, equirectangular, VR180, and omnidirectional stereo cameras are supported and can be configured within Blender.
- The generated JSON file can be imported into Luxenstudio. Each keyframe of the camera transform in the frame sequence in Blender will be a keyframe in Luxenstudio. The exported JSON camera path is baked, where each frame in the sequence is a keyframe. This is to ensure that frame interpolation across Luxenstudio and Blender do not differ.
    <center>
    <img width="800" alt="image" src="https://user-images.githubusercontent.com/9502341/211245108-587a97f7-d48d-4515-b09a-5644fd966298.png">
    </center>
- It is recommended to run the camera path in the Luxenstudio web interface with the Luxen to ensure that the Luxen is visible throughout the camera path.
- The fps and keyframe timestamps are based on the "Frame Rate" setting in the Output Properties in Blender.
- The Luxen representation can also be transformed (position, rotation, and scale) as well as animated.
- The pivot point of the Luxen representation should not be changed
- It is recommended to export a high fidelity mesh as the Luxen representation from Luxenstudio. However if that is not possible or the scene is too large, a point cloud representation also works.
- For compositing, it is recommended to convert the video render into image frames to ensure the Blender and Luxen renders are in sync.
- Currently, dynamic camera focus is not supported.
- Compositing with Blender Objects and VR180 or ODS Renders
  - Configure the Blender camera to be panoramic equirectangular and enable stereoscopy in the Output Properties. For the VR180 Blender camera, set the panoramic longitude min and max to -90 and 90.
  - Under the Stereoscopy panel the Blender camera settings, change the mode to "Parallel", set the Interocular Distance to 0.064 m, and checkmark "Spherical Stereo".

    <center>
    <img width="300" alt="image" src="https://github-production-user-asset-6210df.s3.amazonaws.com/9502341/253217833-fd607601-2b81-48ab-ac5d-e55514a588da.png">
    </center>
- Fisheye and orthographic cameras are not supported.
- Renders with Gaussian Splats are supported, but the point cloud or mesh representation would need to be generated from training a Luxen on the same dataset.
- A walkthrough of this section is included in the tutorial video.

## Create Blender Camera from Luxenstudio JSON Camera Path

<p align="center">
    <img width="800" alt="image" src="https://user-images.githubusercontent.com/9502341/211246016-88bc6031-01d4-418f-8230-fb8c29212200.png">
</p>

1. Expand the "Luxenstudio Camera Generator" tab in the panel. After inputting the Luxen representation, select the JSON Luxenstudio file and click "Create Camera from JSON"

2. A new camera named "LuxenstudioCamera" should appear in the viewport with the camera path and FOV of the input file. This camera's type will match the Luxenstudio input file, except fisheye cameras.

### Additional details

- Since only the camera path, camera type, and FOV are applied on the created Blender camera, the timing and duration of the animation may need to be adjusted.
- Fisheye cameras imported from Luxenstudio are not supported and will default to perspective cameras.
- Animated Luxen representations will not be reflected in the imported camera path animation.
- The newly created camera is not active by default, so you may need to right click and select "Set Active Camera".
- The newly created Blender camera animation is baked, where each frame in the sequence is a keyframe. This is to ensure that frame interpolation across Luxenstudio and Blender do not differ.
- The resolution settings from the input JSON file do not affect the Blender render settings
- Scale of the camera is not keyframed from the Luxenstudio camera path.
- This newly created camera has a sensor fit of "Vertical"

## Compositing Luxen Objects in Luxen Environments

You can composite Luxen objects into a scene with a Luxen background by rendering the cropped Luxen object along with an accumulation render as an alpha mask and compositing that over the background Luxen render.

<p align="center">
    <img width="450" alt="image" src="https://user-images.githubusercontent.com/9502341/232261745-80e36ae1-8527-4256-bbd0-83461e6f4324.jpg">
</p>

1. Import the background Luxen scene as a point cloud (or mesh, but point cloud is preferred for large scenes).

2. Export a cropped Luxen mesh of the Luxen object(s)

   - Open the Luxen object from the Luxenstudio viewer and select "Crop Viewport" and accordingly adjust the Scale and Center values of the bounding box to crop the Luxen scene to around the bounds of the object of interest.

   <center>
   <img width="300" alt="image" src="https://user-images.githubusercontent.com/9502341/232264554-26357747-6f09-4084-9710-dabf60c61909.jpg">
   </center>

   - Copy over the scale and center values into the Export panel and export the Luxen object as a mesh (point cloud will also work but shadows can be rendered if the object is a mesh)

   - Keep note of the scale and center values for the crop. This can be done by creating a new JSON camera path in the editor which will add a crop section towards the end of the file.

   <center>
   <img width="200" alt="image" src="https://user-images.githubusercontent.com/9502341/232264430-0b991e20-838f-4e06-9834-7d1d8c1d0042.png">
   </center>

3. Import the Luxen object representation. Rescale and position the scene and Luxen object and background environment. You can also animate either of them.

4. (Optional) To add shadows of the Luxen object(s)

   - Add a plane representing the ground of the environment. In object properties, select "Shadow Catcher" under Visibility. You may have to switch to the cycles renderer to see the shadow catcher option.

   - In the object properties of the Luxen object, go to the Ray Visibility section and deselect the "Camera" option. This will hide the mesh in the Blender render, but keep its shadow.

   <center>
   <img width="200" alt="image" src="https://user-images.githubusercontent.com/9502341/232265212-ca077af8-fb3a-491f-8d60-304cb9fae57e.png">
   </center>

   - Render the Blender animation with only the shadow of the object on the shadow catcher visible. Render with a transparent background by selecting "Transparent" under the Film Settings in the Render Properties.

5. Go to the Luxenstudio Add-on in Render Properties and expand the "Luxenstudio Path Generator" tab in the panel. Use the object selector to select the Luxen environment representation. Then, select the file path for the output JSON camera path file. Click "Generate JSON file". The output JSON file is named `camera_path_blender.json`. It is recommended to rename this JSON file to keep track of the multiple camera paths that will be used to construct the full render.

6. Generate a Luxenstudio camera path now for the Luxen object. Select the object selector to select the Luxen object. Before generating the new JSON file, you may need to rename the previously generated camera path for the environment or move it to a different directory otherwise the new JSON file will overwrite it. Click "Generate JSON file". The new output JSON file is named `camera_path_blender.json`. You will need to repeat this process for each Luxen object you want to composite in your scene.

7. Render the Luxen of the background environment using the generated camera path for the environment using the Luxenstudio in the command line or terminal.

8. Render the Luxen object

   - Open the recently generated blender Luxenstudio JSON camera path and add the crop parameters to the camera path. This section will be placed towards the end of the Blender Luxenstudio camera path after the `is_cycle` field. This can be done by copying over the crop section from the JSON camera path with the scene crop which was exported earlier. Alternatively, you can enter the crop values manually in this format.
   <center>
   <img width="200" alt="image" src="https://user-images.githubusercontent.com/9502341/232264689-d2e7747c-ce53-425b-810b-1b2954eceb62.png">
   </center>

   - Render the Luxen object using Luxenstudio and the edited camera path in the command line or terminal. This will be the RGB render.

   - Next, render the accumulation render as an alpha mask of the Luxen object by adding the command line argument `--rendered-output-names accumulation` to the render command.

   <center>
   <img width="450" alt="image" src="https://user-images.githubusercontent.com/9502341/232264813-195c970f-b194-4761-843b-983123f128f7.jpg">
   </center>

9. Convert each of the Luxenstudio render videos into an image sequence of frames as PNG or JPG files. This will ensure that the frames will be aligned when compositing. You can convert the video mp4 to an image sequence by creating a Blender Video Editing file and rendering the mp4 as JPGs or PNGs.

10. Composite the Luxen renders in a video editing software such as Adobe Premiere Pro.

    - Place the render of the Luxenstudio background environment at the lowest layer, then place the shadow render of the Luxen object if created.

    - Place the RGB Luxen render of the Luxen object over the environment (and shadow if present) layers and then place the accumulation Luxen object render over the RGB Luxen object render.

    - Apply a filter to use the accumulation render as an alpha mask. In Premiere Pro, apply the effect "Track Matte Key" to the RGB render and select the "Matte" as the video track of the accumulation render and under "Composite Using" select "Matte Luma".

### Additional Details

- The RGB and accumulation renders will need to be rendered for each Luxen cropped object in the scene, but not for the Luxen environment if it is not cropped.
- If you will composite a shadow layer, the quality of the exported mesh of the Luxen object should have enough fidelity to cast a shadow, but the texture doesn't need to be clear.
- If motion tracking or compositing over real camera footage, you can add planes or cubes to represent walls or doorways as shadow catcher or holdout objects. This will composite the shadow layer over the Luxen environment and help create alpha masks.
- The pivot point of the Luxen representations should not be changed.
- A walkthrough of this section is included in the tutorial video.

### Examples

<p align="center">
    <img width="300" alt="image" src="https://user-images.githubusercontent.com/9502341/232274012-27fb912c-3d3e-47b2-bb6b-68abf8f0692a.gif">
    <img width="225" alt="image" src="https://user-images.githubusercontent.com/9502341/232274049-d03e9768-8905-4668-b41b-d8ad4f122829.gif">
</p>

## Implementation Details

For generating the JSON camera path, we iterate over the scene frame sequence (from the start to the end with step intervals) and get the camera 4x4 world matrix at each frame. The world transformation matrix gives the position, rotation, and scale of the camera. We then obtain the world matrix of the Luxen representation at each frame and transform the camera coordinates with this to get the final camera world matrix. This allows us to re-position, rotate, and scale the Luxen representation in Blender and generate the right camera path to render the Luxen accordingly in Luxenstudio. Additionally, we calculate the FOV of the camera at each frame based on the sensor fit (horizontal or vertical), angle of view, and aspect ratio.
Next, we construct the list of keyframes which is very similar to the world matrices of the transformed camera matrix.
Camera properties in the JSON file are based on user specified fields such as resolution (user specified in Output Properties in Blender), camera type (Perspective or Equirectangular). In the JSON file, `aspect` is specified as 1.0, `smoothness_value` is set to 0, and `is_cycle` is set to false. The Luxenstudio render is the fps specified in Blender where the duration is the total number of frames divided by the fps.
Finally, we construct the full JSON object and write it to the file path specified by the user.

For generating the camera from the JSON file, we create a new Blender camera based on the input file and iterate through the `camera_path` field in the JSON to get the world matrix of the object from the `matrix_to_world` and similarly get the FOV from the `fov` fields. At each iteration, we set the camera to these parameters and insert a keyframe based on the position, rotation, and scale of the camera as well as the focal length of the camera based on the vertical FOV input.
