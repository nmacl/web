from flask import Flask, request, redirect, url_for, send_file, render_template
import pandas as pd
import re
import io

app = Flask(__name__)

def update_features_and_benefits(df):
    # Ensure feature and benefit columns are of type object
    for i in range(1, 11):
        df[f'Feature{i}'] = df[f'Feature{i}'].astype(object)
        df[f'Benefit{i}'] = df[f'Benefit{i}'].astype(object)
    
    df['UpdateDescription'] = df['Description'].astype(object)
    
    for index, row in df.iterrows():
        description = row['Description']

        if pd.notna(description):
            # Split into parts before "Features:" and after
            parts = re.split(r'Features:', description, maxsplit=1)
            if len(parts) > 1:
                df.at[index, 'UpdateDescription'] = parts[0].strip()
                after_features = parts[1].strip()
                
                # Split after "Benefits:" to separate Features and Benefits
                feature_parts = re.split(r'Benefits:', after_features, maxsplit=1)
                features_text = feature_parts[0].strip() if len(feature_parts) > 0 else ""
                benefits_text = feature_parts[1].strip() if len(feature_parts) > 1 else ""
                
                # Process Features
                feature_sentences = re.split(r'(?<!\d)\. ?', features_text)
                for i, sentence in enumerate(feature_sentences):
                    stripped_sentence = sentence.strip() + '.'
                    if len(stripped_sentence) > 4 and i < 10:
                        df.at[index, f'Feature{i+1}'] = stripped_sentence
                
                # Process Benefits
                benefit_sentences = re.split(r'(?<!\d)\. ?', benefits_text)
                for i, sentence in enumerate(benefit_sentences):
                    stripped_sentence = sentence.strip() + '.'
                    if len(stripped_sentence) > 4 and i < 10:
                        df.at[index, f'Benefit{i+1}'] = stripped_sentence
            else:
                # If "Features:" is not found, retain description
                df.at[index, 'UpdateDescription'] = description.strip()
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
        content = file.read().decode('utf-8', errors='ignore')
        data = pd.read_csv(io.StringIO(content))
        updated_data = update_features_and_benefits(data)
        output = io.BytesIO()
        updated_data.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name='updated.csv')

if __name__ == '__main__':
    app.run(debug=True)
