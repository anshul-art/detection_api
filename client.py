import requests

def detect_objects(image_path, server_url, output_path):
    url = f"{server_url}/detect"
    
    with open(image_path, "rb") as f:
        files = {"file": (image_path, f, "image/jpeg")}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        with open(output_path, "wb") as out:
            out.write(response.content)
        print(f"Saved to {output_path}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    detect_objects(
        image_path="test.jpg",
        server_url="http://localhost:8000",
        output_path="result.jpg"
    )