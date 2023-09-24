from flask import Flask, request, render_template, send_file
import sys
sys.path.append('singing_transcription')
sys.path.append('midi_backing')
import os
import music_accomp
import midi
import tempfile

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Get the uploaded file
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            # Process the file (replace this with your processing logic)
            # For example, save it to a new file
            processed_filename = 'flask.mid'
            print(uploaded_file)
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, uploaded_file.filename)

            # Save the uploaded file to the temporary directory
            uploaded_file.save(temp_file_path)
            pattern = music_accomp.music_accomp(temp_file_path)
            midi.write_midifile(processed_filename, pattern)
            #uploaded_file.save(processed_filename)
            # Clean up: Delete the temporary directory and file
            os.remove(temp_file_path)
            os.rmdir(temp_dir)
            # Redirect to the result page
            return render_template('result.html', result_file=processed_filename)
            #return send_file(processed_filename, as_attachment=True)

    return render_template('upload.html')

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Generate the path to the processed file
    #processed_dir = 'processed_files'
    #file_path = os.path.join(processed_dir, filename)

    # Serve the file for download
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
