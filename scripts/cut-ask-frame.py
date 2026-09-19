"""Remove the unfilled ask card from the two investor decks.

The ask card is the right half of the founder scene. It reveals on a hard cut a
few frames after the scene settles and stays until the scene crossfades out, so
the edit is: clear the card band, recentre the founder card that is left, and
rebuild both crossfades by blending against the edited frames rather than the
originals. Everything outside the card band, and every other scene, is untouched.
"""
from PIL import Image
import numpy as np

BG = np.array([14, 17, 23], dtype=np.uint8)
SRC = r'C:\Users\houck\Downloads\pitch-gifs\%s.gif'

DECKS = [
    # name, crossfade-in (first, last), stable (first, last), crossfade-out (first, last), band
    ('06-investor-layer-under-every-model', (393, 401), (402, 448), (449, 455), (100, 412)),
    ('07-investor-the-moat-is-the-archive', (355, 363), (364, 404), (405, 411), (94, 420)),
]
CARD_X = (42, 562)          # founder card with margin
CLEAR_X = (30, 1170)        # everything the two cards and their shadows occupy
CAPTION = (615, 655)        # the scene title in the bottom band

# Deck seven titles this scene after the ask, so the title goes with the ask. The
# replacement is lifted pixel for pixel from deck six, which titles the same scene
# after the card that is left. Same design system, same face, size and position,
# so nothing is re-rendered and nothing can drift.
CAPTION_DONOR = ('06-investor-layer-under-every-model', 440)


def load(path):
    im = Image.open(path)
    frames, durations = [], []
    for f in range(im.n_frames):
        im.seek(f)
        frames.append(np.asarray(im.convert('RGB'), dtype=np.uint8).copy())
        durations.append(im.info.get('duration', 80))
    return frames, durations


def recentre(frame, band):
    """Drop the ask card and move the founder card to the middle."""
    y0, y1 = band
    patch = frame[y0:y1, CARD_X[0]:CARD_X[1]].copy()
    frame[y0:y1, CLEAR_X[0]:CLEAR_X[1]] = BG
    w = CARD_X[1] - CARD_X[0]
    x = (frame.shape[1] - w) // 2
    frame[y0:y1, x:x + w] = patch
    return frame


def alpha_of(f, a, b):
    """How far frame f has crossfaded from a to b, by least squares."""
    d = b.astype(np.float64) - a.astype(np.float64)
    n = float((d * d).sum())
    if n == 0:
        return 0.0
    v = float(((f.astype(np.float64) - a.astype(np.float64)) * d).sum()) / n
    return min(1.0, max(0.0, v))


def blend(a, b, t):
    return (a.astype(np.float64) * (1 - t) + b.astype(np.float64) * t).round().astype(np.uint8)


for name, fin, stable, fout, band in DECKS:
    frames, durations = load(SRC % name)
    original = [f.copy() for f in frames]

    for i in range(stable[0], stable[1] + 1):
        recentre(frames[i], band)

    if name.startswith('07'):
        donor, dframe = CAPTION_DONOR
        d = Image.open(SRC % donor)
        d.seek(dframe)
        strip = np.asarray(d.convert('RGB'), dtype=np.int16)[CAPTION[0]:CAPTION[1]]
        strip = np.clip(strip + (frames[stable[0]][640, 1150].astype(np.int16) - strip[25, 1150]),
                        0, 255).astype(np.uint8)
        for i in range(stable[0], stable[1] + 1):
            frames[i][CAPTION[0]:CAPTION[1]] = strip

    # Crossfade in: previous scene to the edited first stable frame.
    a_in, b_in = original[fin[0] - 1], original[stable[0]]
    for i in range(fin[0], fin[1] + 1):
        frames[i] = blend(a_in, frames[stable[0]], alpha_of(original[i], a_in, b_in))

    # Crossfade out: the edited last stable frame to the next scene.
    a_out, b_out = original[stable[1]], original[fout[1] + 1]
    for i in range(fout[0], fout[1] + 1):
        frames[i] = blend(frames[stable[1]], b_out, alpha_of(original[i], a_out, b_out))

    # One palette for the whole deck, so a frame does not shift colour mid-loop.
    sample = Image.fromarray(np.concatenate([frames[i] for i in range(0, len(frames), 7)], axis=0))
    pal = sample.quantize(colors=128, method=Image.MEDIANCUT)
    out = [Image.fromarray(f).quantize(palette=pal, dither=Image.NONE) for f in frames]
    out[0].save('%s.gif' % name, save_all=True, append_images=out[1:],
                duration=durations, loop=0, optimize=True, disposal=1)
    print(name, 'frames', len(out))
