from flask import Flask, request, redirect, url_for, send_file, render_template
import pandas as pd
import re
import io

app = Flask(__name__)

def update_features_v3(df):
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
        data = pd.read_csv(file)
        updated_data = update_features_v3(data)
        output = io.BytesIO()
        updated_data.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, mimetype='text/csv', as_attachment=True, attachment_filename='nike_updated.csv')

if __name__ == '__main__':
    app.run(debug=True)
