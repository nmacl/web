from flask import Flask, request, redirect, url_for, send_file, render_template
import pandas as pd
import re
import io

app = Flask(__name__)

def update_features_v3(df):
    # Ensure feature columns are of type object and initialize UpdateDescription column
    for i in range(1, 11):
        df[f'Feature{i}'] = df[f'Feature{i}'].astype(object)
    df['UpdateDescription'] = df['Description'].astype(object)
    
    for index, row in df.iterrows():
        description = row['Description']

        if pd.notna(description):
            # Split the description into parts before and after "Features:"
            parts = re.split(r'Features:', description, maxsplit=1)
            if len(parts) > 1:
                df.at[index, 'UpdateDescription'] = parts[0].strip()
                features_text = parts[1].strip()
                sentences = re.split(r'(?<!\d)\. ?', features_text)
                feature_columns = []
                feature_index = 1

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
            else:
                df.at[index, 'UpdateDescription'] = description.strip()
    return df

def update_benefits(df):
    # Ensure benefit columns are of type object
    for i in range(1, 11):
        df[f'Benefit{i}'] = df[f'Benefit{i}'].astype(object)
    
    for index, row in df.iterrows():
        description = row['Description']

        if pd.notna(description):
            # Process only the Benefits section
            benefit_parts = re.split(r'Benefits:', description, maxsplit=1)

            if len(benefit_parts) > 1:
                benefits_text = benefit_parts[1].strip()
                benefit_sentences = re.split(r'(?<!\d)\. ?', benefits_text)
                
                benefit_columns = []
                benefit_index = 1
                for sentence in benefit_sentences:
                    stripped_sentence = sentence.strip() + '.'
                    if len(stripped_sentence) > 4 and benefit_index <= 10:
                        benefit_columns.append(stripped_sentence)
                        benefit_index += 1

                for i, benefit in enumerate(benefit_columns):
                    df.at[index, f'Benefit{i+1}'] = str(benefit)

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
        updated_data = update_features_v3(data)  # Process Features first
        updated_data = update_benefits(updated_data)  # Then process Benefits
        output = io.BytesIO()
        updated_data.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name='updated.csv')

if __name__ == '__main__':
    app.run(debug=True)
