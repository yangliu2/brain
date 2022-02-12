# Brain
Trying to find a way to simulate the human brain

# Principles
1. Human brain can be separated to a cache and the main memory. The cache will 
have constant access for the brain and will be faster to search to generate an 
action or formulate a reponse. 
1. Periodically, the memory will be scanned to see if new things should be put 
into the cache. This could be an update to promote the most recently popular 
process and the least recently used item in the cache should be demoted to the 
main memory.
1. To use an unsupervised learning approach, the clusters in the cache should 
have a small constant size and use least recently used method to retain useful 
things. The purpose for the small cache is so the clustering or other 
unsupervised method is efficient enough. 