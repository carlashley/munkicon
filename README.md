This is a collection of conditional items scripts for munki that can also be used for "on device" conditions that might be beneficial in other deployment systems.

## DISCLAIMER
This is experimental and provided _as is_ with no warranty, or guaranteed support.

Please test that this works for you in your environment.

## Building a package
After cloning, run `./build.sh` and provide a password for `sudo` when prompted.

The resulting package is generated in `./dist/pkg/`.

*Note* if you need to deploy this with a specific Python shebang, such as the munki `/usr/local/munki/munki-python`, simply build with the path as the only argument:
```
./build.sh /usr/local/munki/munki-python
```

## Binaries
All binaries called by the processors exist in macOS 10.15.7+. No intention to make these backwards compatible with older macOS versions.


## Usage
`munkicon` can be dropped directly into the munki conditions folder (`/usr/local/munki/conditions/`), however the prebuilt package installs the `munkicon` processor to `/usr/local/bin/munkicon` by default.

It is recommended to use a shell script in the munki conditions folder that calls `munkicon`. This will provide flexibility in running all processors (no command line flags, or just run specific processors).

For example, to run all processors:
```
/usr/local/bin/munkicon
```

To run specific processors (see Command Line Arguments below for usage):
```
/usr/local/bin/munkicon --kexts --user-accts --system-setup
```

### Command line arguments
```
[carl@munkicon]:bin # ./munkicon -h
usage: munkicon [-h] [--certificates] [--filevault] [--kexts] [--mdm-enrolled] [--pppcp] [--profiles] [--python] [--system-exts] [--system-setup] [--user-accts] [--purge]
                [--dest [path]] [-v, --version]

optional arguments:
  -h, --help      show this help message and exit
  --certificates  process certificate conditions from system keychain
  --filevault     process FileVault conditions
  --kexts         process kext conditions
  --mdm-enrolled  process MDM enrolled conditions
  --pppcp         process PPPCP conditions
  --profiles      process profiles conditions
  --python        process python conditions
  --system-exts   process system extension conditions
  --system-setup  process sytem setup conditions
  --user-accts    process user account conditions
  --purge         purges all existing information
  --dest [path]   output conditions to specific destination plist
  -v, --version   show program's version number and exit
```

## Conditions
For more details about each condition processor, see the [wiki](https://github.com/carlashley/munkicon/wiki/Processors)
