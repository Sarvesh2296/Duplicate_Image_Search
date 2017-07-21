# Duplicate_Image_Search
Phash creates a unique hexadecimal representation of an image. This representaion is color invariant, scale invariant and rotation invariant.

Perceptual hash algorithms describe a class of comparable hash functions. Features in the image are used to generate a distinct (but not unique) fingerprint, and these fingerprints are comparable.

Perceptual hashes are a different concept compared to cryptographic hash functions like MD5 and SHA1. With cryptographic hashes, the hash values are random. The data used to generate the hash acts like a random seed, so the same data will generate the same result, but different data will create different results. Comparing two SHA1 hash values really only tells you two things. If the hashes are different, then the data is different. And if the hashes are the same, then the data is likely the same. (Since there is a possibility of a hash collision, having the same hash values does not guarantee the same data.) In contrast, perceptual hashes can be compared -- giving you a sense of similarity between the two data sets.

Phash creates the hexadecimal by following these steps:
1) Rescales the image to a smaller dimension to remove the finer details of an image.
2) Convert the image to grayscale to make the further computations easier, moreover, this makes the phash algorithm color invariant
3) Compute the average DCT of the image and then construct the 64 bit hash based on whether the DCT values are above or below the average DCT value
4)Convert the hash from this binary array 
We use the Discrete Cosine Transform instead of finding the average.

Its contains two codes having small difference. 
1) A dictionary is created which is then saved in a csv file
2) The response is added to Redis Database after every hash is created
