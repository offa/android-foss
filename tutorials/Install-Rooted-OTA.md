# Installation of OTA on a Rooted Device

The installation of OTA updates often fails if the device has been rooted. Though it's still possible – without data loss. This guide shows how, using *TWRP* and *Magisk*.

***IMPORTANT:** Before you start **backup** everything that's important!*

-------------------------------------

## Prerequisite

1. The Update file of the version that's running on the device (*NOT* the update you want to install)
1. [**TWRP**](https://twrp.me/) for your device
1. [**Magisk**](https://forum.xda-developers.com/apps/magisk/official-magisk-v7-universal-systemless-t3473445)
1. *ADB* and *Fastboot* inclusive developer mode the device

Don't forget to check the checksums of all files.

Doing the update isn't that difficult: Reset some system partitions, install OTA, refresh *TWPR* and *Magisk*, done. There are two versions of this guide: The short version is just a list of steps, while the long version contains each step and the commands necessary.


## Short Version

1. Download the Update *current installed*
1. Enable USB Debugging
1. Boot to Bootloader
1. Flash *recovery*, *system* and *boot* images
1. Reboot
1. Flash *TWRP*
1. Boot to Recovery
1. Install *Magisk*
1. Reboot


-------------------------------------

## Long Version

At first double check your backups and the prerequisites listed above. 


