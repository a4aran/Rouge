# Logs

## [Current Verison](#version-01su01)

## Version 0.0.1su.1
Added ***Parallax*** and a way to make ***Custom Buttons***<br>
Also changed ***globals.py*** to ***engine_constants.py*** 
which led to requirement of ***window_size.py*** outside the engine
<br>
<br>
*window_size.py:*
```
width = [window widht specified by user]
height = [window height specified by user]
```
<br>
This version is semi-updatable, which means that to update engine's version in your project 
you need to copy the files in <i><b>Illusion</b></i> package

## Version 0.0.1su.1b
Small addition and some fixes.

Added **_create_ui_** method to scene so you don't need to manually append new UIs.
<br>
<br>
Fixed the **data** in UI so that it actually works, I deleted the field from UI so now only **data** field in UI is in GUI subclass. Also added methods that allow editing the data, **_data_** in UI which returns the data field from GUI and **_delete_var_from_data_** which allows easy deletion.
<br>
<br>
Made **_parallax_** 'responsive', as in you can change the speed and things like that.

## Version 0.0.1su.2
Added better system for music by implementing _**Music Manager**_

## Version 0.0.1su.2b _hotfix_
Added _**resync_volume**_ method so that the muting is applied correctly

## Version 0.0.2su
All files that are important for the engines work come inside the _**Illusion**_ package.<br>
Only exception are **_game.py_** and **_window_size.py_** as they are meant ot be edited by the user.

## Version 0.0.2su.1
Added new class **_GlobalsObjects_** whose object is automatically created in _**GameManager**_ similarly to classes from _**importer.py**_.
<br>
<br>
Made _**UI**_ work better in scenes. Added method to _**scene**_ called **_get_data_from_uis_**, which changes the scene's _change scene_ related **data**.
<br>
<br>
Fixed a bug in _**SceneManager**_ where it would change the scene to _should_change_scene_ data of the scene instead of _scene_to_change_to_.
<br>
<br>
Fixed a bug/oversight where the **_Scene Change Button_** didn't have **rendered_text** in their constructor.
<br>
<br>
Added **current_track** field to the _**MusicManager**_

## Version 0.0.2.1b _bugfix_
You can now get the volume value from **_MusicManager_** and see the **id** of previous scene. The _**on_changed_to**_ method of **_Scene_** now accepts mentioned **id** of previous scene.
<br>
Added **_resync_volume_** to methods that edit volume. Fixed **_change_volume_by_**'s method. 

## Version 0.0.3su
I improved the text renderer and all things connected to displaying text in general.

What I exactly changed is how the **_TextRenderer_** objects are stored. Before you would have to create a new variable in the **_game_** but now, you can call an **_add_font_** of the _**GlobalObjects**_ class. It stores those **_TextRenderer_**s in a dict so it is easy to access unlike before.

Other than that I added new class to the **_HUD_** which is **_TextDisplay_** which is just an easy way to display text. It allows to display said text in multiple lines as well as it allows the user to change most of the properties of the object whenever they want.

I also changed the **_Button_** so that it is easier to make buttons with text.

## Version 0.0.3su.1
Added a **_Hoverable_** class into the **_c_helper_** which allows you to easily make objects with hover detection.

Added actual layering of UIs by making a new dict in **_Scene_** called **bg_uis** which stands for **background UIs**. I also added methods and edited existing to make it work.

## Version 0.1su
Added a new dict into **_GlobalObjects_** for custom objects.

Changed the way importer works with images, so now you can call a method that will return the surface instead of methods that can only import to the local storage of importer. 

Made _**change_scene**_ method of **_SceneManager_** public.

Added a way for **_TextDisplay_** to have static y pos.


## Version 0.1su.0.1
I added a check for initializing the **_mixer_** so that the game works on devices without audio hardware.

**For now development stops**

## Version 0.1su.1
Made it possible to easily export the project as _.exe_ file using `pyinstaller run.py --add-data="assets:assets"`. After running that in _cmd_ you'll need to take the _assets_ folder out of the *_internal* folder  and into the folder with _.exe_ file.

Added easy customizability to the project using files like *app_data* and *engine_settings*.

Made **UIs** hidable.
