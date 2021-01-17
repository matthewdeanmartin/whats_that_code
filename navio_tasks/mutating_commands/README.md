These commands change the source code.

- On a build server, needing to change code should break the build.
- After changing code, the new code needs to be checked in.
- Mutating should happen before unit tests.
- Black should be the final mutator because only one formatter can "win"
