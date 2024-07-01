from flask import Flask, request, redirect, url_for, send_file, render_template
import pandas as pd
import re
import io

app = Flask(__name__)

def update_features_v3(df):
    # Ensure feature columns are of type object
    for i in range(1, 11):
        df[f'Feature{i}'] = df[f'Feature{i}'].astype(object)
    
    for index, row in df.iterrows():
        description = row['Description']

        if pd.notna(description):
            description = description.replace("Features:", "")
            sentences = re.split(r'(?<!\d)\. ?', description)
            feature_columns = ["<strong>Features:</strong>"]
            feature_index = 2

            percent_sentence_found = False
            for sentence in sentences:
                if '%' in sentence and not percent_sentence_found:
                    feature_columns.append(sentence.strip() + '.')
                    percent_sentence_found = True
                else:
                    stripped_sentence = sentence.strip() + '.'
                    if len(stripped_sentence) > 4 and feature_index <= 10:
                        feature_columns.append(stripped_sentence)
                        feature_index += 1

            for i, feature in enumerate(feature_columns):
                df.at[index, f'Feature{i+1}'] = str(feature)
    return df

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        data = None
        try:
            # Try reading with utf-8 encoding
            data = pd.read_csv(file, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                # Fallback to ISO-8859-1 encoding
                file.seek(0)  # Reset file pointer to the beginning
                data = pd.read_csv(file, encoding='ISO-8859-1')
            except Exception as e:
                return f"Failed to read the file with both utf-8 and ISO-8859-1 encodings: {str(e)}", 400

        if data is None or data.empty:
            return "Failed to read the file: No columns to parse from file", 400

        try:
            updated_data = update_features_v3(data)
            output = io.BytesIO()
            updated_data.to_csv(output, index=False)
            output.seek(0)
            return send_file(output, mimetype='text/csv', as_attachment=True, download_name='nike_updated.csv')
        except Exception as e:
            return f"An error occurred while processing the file: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
