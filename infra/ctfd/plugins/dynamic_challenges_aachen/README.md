# Aachen Scoring Plugin

Adds a third decay function (`aachen`) to CTFd dynamic challenges alongside the
built-in `linear` and `logarithmic` options.

## Curve shape

The Aachen function is a convex sigmoid. It drops faster for early solves and
then tapers toward `minimum`, avoiding the steeper late cliff from the default
parabolic behavior.

## Usage

Set this in a dynamic challenge `challenge.yml`:

```yaml
extra:
  initial: 500
  minimum: 30
  decay: 30
  function: aachen
```

`decay` remains in metadata for compatibility, even though the Aachen function
does not use it directly.

## Tuning

Adjust constants in `__init__.py`:

- `AACHEN_INFLECTION`
- `AACHEN_STEEPNESS`
