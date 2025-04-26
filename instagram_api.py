from flask import Flask, request, jsonify
import os
import instaloader

app = Flask(__name__)

@app.route('/api/instagram', methods=['POST'])
def download_instagram():
    data = request.get_json()
    url = data.get('url')

    try:
        loader = instaloader.Instaloader(dirname_pattern='downloads', save_metadata=False)
        shortcode = url.split("/")[-2]
        loader.download_post(instaloader.Post.from_shortcode(loader.context, shortcode), target=shortcode)

        files = os.listdir(shortcode)
        video_file = next((f for f in files if f.endswith('.mp4')), None)

        if video_file:
            return jsonify({
                "success": True,
                "download_url": f"http://127.0.0.1:5000/downloads/{shortcode}/{video_file}"
            })
        else:
            return jsonify({"success": False, "error": "Video not found in post"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
