import kagglehub

# Download latest version
path = kagglehub.dataset_download("moazeldsokyx/bbc-news")

print("Path to dataset files:", path)