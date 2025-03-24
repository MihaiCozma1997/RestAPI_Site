import requests

# API endpoint for a specific post
post_id = 1
url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"

# Data to update
updated_post = {
    "id": post_id,  # ID must be included
    "title": "Updated Title",
    "body": "This post has been updated!",
    "userId": 1
}

# Send PUT request
response = requests.put(url, json=updated_post)

# Print response
print("Updated Post:", response.json())

# Send DELETE request
response = requests.delete(url)

# Check status code (should be 200 or 204 if successful)
if response.status_code in [200, 204]:
    print(f"Post {post_id} deleted successfully!")
else:
    print("Failed to delete post:", response.status_code)

