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
