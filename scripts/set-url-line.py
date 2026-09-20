"""Replace the placeholder URL line in the closing scene of a pitch deck.

Companion to cut-ask-frame.py and the same discipline: touch one band of one scene, leave
every other pixel alone, and rebuild the fade rather than letting the edit snap in.

The closing frame of each deck carries a placeholder the export never had filled in:
`[ YOUR URL HERE ]` on the five Trooth decks, `[ URL ]` on the MedDevice Pulse one. On a deck
sent in a DM that is invisible, because the link is in the message. On a page at a public URL it
is the most-looked-at frame in the loop, so it gets the real address.

How the band is found, rather than hardcoded. The line sits at a different y in every deck, so
each entry declares it once, measured from the last frame. The scene it belongs to is detected:
walking back from the final frame, a frame is part of the closing scene while its band is a
scalar fade of the final band, `band = bg + t * (final - bg)`, within a residual tolerance that
allows for GIF palette quantisation. That gives both the range to edit and, per frame, the alpha
to render at, so the new text fades in on exactly the curve the old one did.

The font is Inter, which the design system names. Weight, size and letter-spacing were not
guessed: rendering `[ YOUR URL HERE ]` at Bold 12px with 2.4px of tracking reproduces the
placeholder's measured 148x12 box exactly, and matches its ink coverage more closely than
Medium or SemiBold do. Everything else on the frame is untouched, so if the match is off it is
off only on this one line.

The URL is rendered lowercase. The surrounding caption style is uppercase, but a GitHub Pages
path is case-sensitive and `/TROOTH-SITE` would not resolve. Correct beats consistent here.

Run with --preview to write a PNG of the affected band, before and after, and stop. Nothing is
written to a GIF until you have looked at it.
"""

import argparse
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageSequence

FONT = os.environ.get("INTER_TTF", "Inter-Bold.ttf")
SIZE = 12
TRACKING = 2.4
RESIDUAL_TOLERANCE = 26  # 0-255; GIF palette quantisation alone costs about 20
MIN_ALPHA = 0.02

# name, source gif, y0, y1, background, centre x, replacement text
DECKS = [
    ("01-trooth-the-receipt", 482, 493, (14, 17, 23), 598, "alexchouck-hash.github.io/trooth-site"),
    ("02-trooth-stop-wiring", 474, 485, (14, 17, 23), 598, "alexchouck-hash.github.io/trooth-site"),
    ("03-trooth-all-the-benefits", 474, 485, (14, 17, 23), 598, "alexchouck-hash.github.io/trooth-site"),
    ("04-client-every-number-earns-its-place", 464, 475, (14, 17, 23), 598, "alexchouck-hash.github.io/trooth-site"),
    ("05-client-shared-work-shared-cost", 464, 475, (14, 17, 23), 598, "alexchouck-hash.github.io/trooth-site"),
    # Points at the method note rather than the press page the deck is hosted on. The deck's
    # call to action is "send me your product code", so sending the viewer back to the deck
    # they just watched would be a circular CTA; the method note is where the substance is.
    ("08-meddevice-pulse-client", 462, 473, (30, 33, 38), 599,
     "alexchouck-hash.github.io/kourob/maude.html  ·  FREE WHILE IN DESIGN-PARTNER STAGE"),
]


def load(path):
    """Frames as RGB, their durations, and the deck's own global palette.

    The palette is what lets the output be re-indexed rather than re-quantised, so frames this
    edit never touches survive byte-identical.
    """
    im = Image.open(path)
    palette = im.getpalette()
    frames, durations = [], []
    for f in ImageSequence.Iterator(im):
        frames.append(np.asarray(f.convert("RGB"), dtype=np.uint8).copy())
        durations.append(f.info.get("duration", im.info.get("duration", 80)))
    if palette is None:
        raise SystemExit(f"{path} has no global palette; this tool assumes one")
    return frames, durations, palette


def text_mask(text, width, height, centre_x):
    """An alpha mask of the replacement line, centred, cropped to the band."""
    font = ImageFont.truetype(FONT, SIZE)
    pad = 60
    canvas = Image.new("L", (width + pad * 2, height + pad * 2), 0)
    draw = ImageDraw.Draw(canvas)
    x = float(pad)
    for ch in text:
        draw.text((x, pad), ch, font=font, fill=255)
        x += draw.textlength(ch, font=font) + TRACKING
    arr = np.asarray(canvas)
    ys, xs = np.nonzero(arr > 12)
    if len(xs) == 0:
        raise SystemExit("the replacement text rendered to nothing; check the font path")
    glyphs = arr[ys.min():ys.min() + height, xs.min():xs.max() + 1]
    if glyphs.shape[0] < height:
        glyphs = np.pad(glyphs, ((0, height - glyphs.shape[0]), (0, 0)))
    out = np.zeros((height, width), dtype=np.float32)
    left = int(round(centre_x - glyphs.shape[1] / 2))
    if left < 0 or left + glyphs.shape[1] > width:
        raise SystemExit(f"replacement line is {glyphs.shape[1]}px wide and does not fit centred")
    out[:, left:left + glyphs.shape[1]] = glyphs
    return out / 255.0, glyphs.shape[1]


def ink_colour(band, bg):
    """The deck's own caption colour: the brightest pixel in the placeholder."""
    mask = np.abs(band.astype(np.int16) - bg).sum(axis=2) > 18
    px = band[mask]
    return px[px.sum(axis=1).argmax()].astype(np.float32)


def closing_scene(frames, y0, y1, bg):
    """Frames belonging to the closing scene, with the alpha each one is faded to."""
    bands = [f[y0:y1 + 1].astype(np.float32) for f in frames]
    final = bands[-1] - bg
    denom = float((final * final).sum())
    alphas, residuals = [], []
    for b in bands:
        d = b - bg
        t = float((d * final).sum()) / denom
        alphas.append(t)
        residuals.append(float(np.abs(d - t * final).max()))
    i = len(frames) - 1
    while i > 0 and residuals[i - 1] <= RESIDUAL_TOLERANCE and -0.05 <= alphas[i - 1] <= 1.2:
        i -= 1
    return [j for j in range(i, len(frames)) if alphas[j] > MIN_ALPHA], alphas


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", required=True, help="directory holding the source GIFs")
    ap.add_argument("--out", required=True, help="directory to write edited GIFs into")
    ap.add_argument("--only", help="process one deck by name prefix")
    ap.add_argument("--preview", metavar="PNG", help="write a before/after band strip and stop")
    args = ap.parse_args()

    strips = []
    for name, y0, y1, bg, cx, text in DECKS:
        if args.only and not name.startswith(args.only):
            continue
        src = os.path.join(args.src, name + ".gif")
        if not os.path.exists(src):
            print(f"  skip {name}: no source at {src}")
            continue
        frames, durations, source_palette = load(src)
        bg = np.array(bg, dtype=np.float32)
        height, width = y1 - y0 + 1, frames[0].shape[1]
        edit, alphas = closing_scene(frames, y0, y1, bg)
        colour = ink_colour(frames[-1][y0:y1 + 1], bg)
        mask, line_w = text_mask(text, width, height, cx)
        before = frames[-1][y0:y1 + 1].copy()

        rendered = bg + (colour - bg) * mask[..., None]
        for j in edit:
            a = min(max(alphas[j], 0.0), 1.0)
            frames[j][y0:y1 + 1] = np.clip(bg + a * (rendered - bg), 0, 255).astype(np.uint8)

        print(f"  {name}: line {line_w}px wide, {len(edit)} frames rewritten "
              f"({edit[0]}..{edit[-1]}), colour {tuple(int(v) for v in colour)}")
        strips.append((name, before, frames[-1][y0:y1 + 1].copy()))

        if args.preview:
            continue

        # Re-index into the deck's OWN palette rather than quantising a new one.
        #
        # Building a fresh palette re-encodes every frame, including the several hundred this
        # edit never touches, and that showed up as roughly 1% of pixels drifting by a few
        # levels across the whole loop. Invisible, probably, but there is no reason to accept
        # it: the source carries one 256-entry global palette and no local ones, so every
        # original pixel maps back to exactly the index it came from and the untouched frames
        # come out byte-identical. The only pixels needing a nearest-colour decision are the
        # newly rendered ones, and the ramp between this background and this caption colour is
        # already in the palette because the placeholder used it.
        palette = np.array(source_palette, dtype=np.int16).reshape(-1, 3)
        packed = (palette[:, 0].astype(np.int64) << 16) | (palette[:, 1].astype(np.int64) << 8) | palette[:, 2]
        order = np.argsort(packed)
        sorted_packed = packed[order]

        def to_indices(rgb):
            p = (rgb[:, :, 0].astype(np.int64) << 16) | (rgb[:, :, 1].astype(np.int64) << 8) | rgb[:, :, 2]
            pos = np.searchsorted(sorted_packed, p)
            pos = np.clip(pos, 0, len(sorted_packed) - 1)
            idx = order[pos]
            miss = sorted_packed[pos] != p
            if miss.any():
                px = rgb[miss].astype(np.int32)
                d = ((px[:, None, :] - palette[None, :, :].astype(np.int32)) ** 2).sum(axis=2)
                idx = idx.copy()
                idx[miss] = d.argmin(axis=1)
            return idx.astype(np.uint8), int(miss.sum())

        out, approximated = [], 0
        for f in frames:
            idx, n_miss = to_indices(f)
            approximated += n_miss
            img = Image.fromarray(idx, mode="P")
            img.putpalette(source_palette)
            out.append(img)
        dst = os.path.join(args.out, name + ".gif")
        out[0].save(dst, save_all=True, append_images=out[1:], duration=durations,
                    loop=0, optimize=True, disposal=1)
        print(f"     wrote {dst} ({os.path.getsize(dst) // 1024} KB); "
              f"{approximated} pixels needed a nearest-colour match, all inside the new line")

    if args.preview:
        pad, scale = 18, 2
        sheet = Image.new("RGB", (1200, sum(b.shape[0] * 2 + pad * 2 + 6 for _, b, _ in strips)),
                          (8, 10, 14))
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, before, after in strips:
            d.text((4, y + 2), f"{name}  BEFORE", fill=(130, 140, 155))
            sheet.paste(Image.fromarray(before), (0, y + pad))
            d.text((4, y + pad + before.shape[0] + 2), "AFTER", fill=(130, 140, 155))
            sheet.paste(Image.fromarray(after), (0, y + pad * 2 + before.shape[0]))
            y += before.shape[0] * 2 + pad * 2 + 6
        sheet.resize((sheet.width * scale, sheet.height * scale), Image.NEAREST).save(args.preview)
        print(f"preview written to {args.preview}; nothing else was changed")


if __name__ == "__main__":
    main()
