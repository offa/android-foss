# OTA Update on a Rooted Device

The installation of ***OTA*** updates often fails if the device has been **rooted**. Though it's still **possible** – without loosing any data. This guide shows how, using ***TWRP*** and ***Magisk***.

***WARNING:** Before you start **backup** everything that's important! Proceed at own risk!*

## Table of Contents

* [Prerequisite](#-prerequisite-)
* [Short Version](#-short-version-)
* [Long Version](#-long-version-)
    * [Step 1 – Preparation](#step-1--preparation)
    * [Step 2 – Flash System Images](#step-2--flash-system-images)
    * [Step 3 – Install *OTA*](#step-3--install-ota)
    * [Step 4 – Install *TWRP*](#step-4--install-twrp)
    * [Step 5 – Install *Magisk*](#step-5--install-magisk)
    * [Step 6 – Done](#step-6--done)
* [Further information](#-further-information-)

-------------------------------------

## – Prerequisite –

1. The Update file of the version that's *already running* on the device (*NOT* the update you want to install)
1. [**TWRP**](https://twrp.me/) for your device
1. [**Magisk**](https://forum.xda-developers.com/apps/magisk/official-magisk-v7-universal-systemless-t3473445)
1. ***ADB*** and ***Fastboot*** inclusive *Developer Mode* enabled on the device

Don't forget to check the checksums of all files.

Doing the update isn't that difficult: Reset some system partitions, install ***OTA***, refresh ***TWPR*** and ***Magisk***, done. There are two versions of this guide: The *short version* is just a list of steps, while the *long version* explains each step and the commands necessary.

-------------------------------------

## – Short Version –

1. Download the Update *current installed*
1. Enable USB Debugging
1. Boot to Bootloader
1. Flash *recovery*, *system* and *boot* images
1. Reboot
1. Install OTA
1. Flash ***TWRP***
1. Boot to Recovery
1. Install ***Magisk***
1. Reboot

-------------------------------------

## – Long Version –

At first double check your backups and the prerequisites listed above.

### Step 1 – Preparation

#### Copy *Magisk* to your device

Copy (or download) ***Magisk*** Zip to your device. It doesn't matter if it's on the internal or SD memory, just place it somewhere you can find it again later. You can do this step at any later time too.

#### Stock files of current running version

Download the update file for the version already running on your device – *not* the version you want to install. Given you are running on v1.2.3 and want to update to v1.2.4, you need the v1.2.3 file.

Unpack the downloaded file, you need: `recovery.img`, `system.img` and `boot.img`.

#### Enable USB Debugging

Connect the device to your computer through USB and enable *USB Debugging* on the device.

### Step 2 – Flash System Images

Open a terminal and use these commands to flash the necessary partitions (don't type the `>`):

```sh
# Check if device is recognized
> adb devices

# Boot into bootloader
> adb reboot bootloader

# Check device again in Bootloader
> fastboot devices

# Flash recovery image
> fastboot flash recovery recovery.img

# Flash system image
> fastboot flash system system.img

# Flash boot image
> fastboot flash boot boot.img

# Reboot device
> fastboot reboot
```

### Step 3 – Install *OTA*

Install the ***OTA*** as usual on the device. The update will reboot automatically. Once this is done check that the installed version is correct and your system is up to date.

### Step 4 – Install *TWRP*

Flash ***TWRP*** using ***ADB***. The image typically has a device specific name (eg. `twrp-[version]-[device].img`), for simplification `TWRP.img` is used here.

```sh
# Check if device is recognized
> adb devices

# Boot into bootloader
> adb reboot bootloader

# Check device again in Bootloader
> fastboot devices

# Flash TWRP
> fastboot flash recovery TWRP.img

# Reboot device
> fastboot reboot
```

#### Boot into *TWRP*

When the last command restarts the device, use the *Volume Keys* to navigate. Select boot into *"Recovery"*. ***TWRP*** will show up then.

### Step 5 – Install *Magisk*

From the ***TWRP*** menu select *"Install"* and install the ***Magisk*** Zip. Reboot afterwards.

**Note:** *It's a good chance to clear the Dalvik-Cache at this point – but that's fully optional.*

### Step 6 – Done

Once back in your system make sure everything works fine, you are running the latest version and root is enabled. Just one last step: Disable *USB Debugging*.

That's it!

-------------------------------------

## – Further information –

* [Magisk – OTA Upgrade Guide](https://topjohnwu.github.io/Magisk/ota.html)
* [A manual OTA for rooted hammerheads, quasi](https://gist.github.com/eyecatchup/ec0a852428c19705380e)
