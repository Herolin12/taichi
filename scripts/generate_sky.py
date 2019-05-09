import sys
import array
import OpenEXR
import Imath
import numpy as np
import cv2

# Open the input file
file = OpenEXR.InputFile(sys.argv[1])

# Compute the size
dw = file.header()['dataWindow']
sz = (dw.max.y - dw.min.y + 1, dw.max.x - dw.min.x + 1)

# Read the three color channels as 32-bit floats
FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
(R,G,B) = [array.array('f', file.channel(Chan, FLOAT)).tolist() for Chan in ("R", "G", "B") ]

R = np.array(R).reshape(sz)
G = np.array(G).reshape(sz)
B = np.array(B).reshape(sz)

img = np.stack([R, G, B], axis=2)[:sz[0] // 2]
l = 0.2126 * img[:,:,0] + 0.715 * img[:,:,1] + 0.072 * img[:, :,2]
sz = (sz[0] // 2, sz[1])
print(sz)
for i in range(0, sz[0]):
    l[sz[0] - i - 1] *= np.sin((i + 0.5) / sz[0] * np.pi / 2)
l = l.flatten()
l /= np.sum(l)

nsamples = 1024

cv2.imshow('sky', img[:, :, ::-1])
cv2.waitKey(1)

choices = np.random.choice(list(range(len(l))), nsamples, p=l)
print(choices)

# u, v, r, g, b
output = np.ndarray(shape=(nsamples, 5), dtype=np.uint32)
for i in range(nsamples):
    c = choices[i]
    u, v = c // sz[1], c % sz[1]
    output[i, 0] = u
    output[i, 1] = v
    output[i, 2:5] = img[u, v] * (1 << 20) / l[c]

output.tofile("sky_samples.bin")
(img.astype(np.float32) / np.max(img) * (1 << 20)).astype(np.uint32).tofile("sky_map.bin")
