import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC  # Import SVM
from sklearn.decomposition import LatentDirichletAllocation  # Import LDA
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
import pickle
import os
import numpy as np

def train_svm_model(dataset_path="../dataset/dataset.csv", models_dir="../models/"):
    """
    Train SVM model untuk prediksi status dan promo
    """
    try:
        # Load dataset
        df = pd.read_csv(dataset_path)
        
        # Preprocessing text features
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Combine text features (sesuaikan dengan kolom dataset Anda)
        text_features = df['conversation_text'].fillna('')  # Ganti dengan nama kolom yang sesuai
        X_text = vectorizer.fit_transform(text_features)
        
        # Target variables
        y_status = df['status'].fillna('Unknown')  # Ganti dengan nama kolom yang sesuai
        y_promo = df['promo_type'].fillna('Tidak Ada Promo')  # Ganti dengan nama kolom yang sesuai
        
        # Split data
        X_train, X_test, y_status_train, y_status_test, y_promo_train, y_promo_test = train_test_split(
            X_text, y_status, y_promo, test_size=0.2, random_state=42
        )
        
        # Train SVM models
        print("Training SVM model untuk status...")
        svm_status = SVC(kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42)
        svm_status.fit(X_train, y_status_train)
        
        print("Training SVM model untuk promo...")
        svm_promo = SVC(kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42)
        svm_promo.fit(X_train, y_promo_train)
        
        # Evaluate models
        status_pred = svm_status.predict(X_test)
        promo_pred = svm_promo.predict(X_test)
        
        print(f"SVM Status Accuracy: {accuracy_score(y_status_test, status_pred):.4f}")
        print(f"SVM Promo Accuracy: {accuracy_score(y_promo_test, promo_pred):.4f}")
        
        # Save models
        os.makedirs(models_dir, exist_ok=True)
        
        with open(f"{models_dir}/svm_status.pkl", 'wb') as f:
            pickle.dump(svm_status, f)
            
        with open(f"{models_dir}/svm_promo.pkl", 'wb') as f:
            pickle.dump(svm_promo, f)
            
        with open(f"{models_dir}/vectorizer_svm.pkl", 'wb') as f:
            pickle.dump(vectorizer, f)
        
        print("SVM models saved successfully!")
        return svm_status, svm_promo, vectorizer
        
    except Exception as e:
        print(f"Error training SVM model: {e}")
        return None, None, None

def train_lda_model(dataset_path="../dataset/dataset.csv", models_dir="../models/", n_topics=10):
    """
    Train LDA model untuk topic modeling dan klasifikasi berdasarkan topik
    """
    try:
        # Load dataset
        df = pd.read_csv(dataset_path)
        
        # Preprocessing text features
        vectorizer = CountVectorizer(
            max_features=1000, 
            stop_words='english',
            min_df=2,  # Ignore terms that appear in less than 2 documents
            max_df=0.8  # Ignore terms that appear in more than 80% of documents
        )
        
        # Combine text features (sesuaikan dengan kolom dataset Anda)
        text_features = df['conversation_text'].fillna('')  # Ganti dengan nama kolom yang sesuai
        X_text = vectorizer.fit_transform(text_features)
        
        # Train LDA model untuk topic discovery
        print(f"Training LDA model dengan {n_topics} topik...")
        lda_model = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=100,
            learning_method='batch'
        )
        lda_topics = lda_model.fit_transform(X_text)
        
        # Create topic-based features untuk classification
        topic_features = lda_topics  # Use topic probabilities as features
        
        # Target variables
        y_status = df['status'].fillna('Unknown')  # Ganti dengan nama kolom yang sesuai
        y_promo = df['promo_type'].fillna('Tidak Ada Promo')  # Ganti dengan nama kolom yang sesuai
        
        # Split data
        X_train, X_test, y_status_train, y_status_test, y_promo_train, y_promo_test = train_test_split(
            topic_features, y_status, y_promo, test_size=0.2, random_state=42
        )
        
        # Train classifiers menggunakan topic features
        print("Training classifier berdasarkan LDA topics untuk status...")
        lda_status_clf = LogisticRegression(random_state=42, max_iter=1000)
        lda_status_clf.fit(X_train, y_status_train)
        
        print("Training classifier berdasarkan LDA topics untuk promo...")  
        lda_promo_clf = LogisticRegression(random_state=42, max_iter=1000)
        lda_promo_clf.fit(X_train, y_promo_train)
        
        # Evaluate models
        status_pred = lda_status_clf.predict(X_test)
        promo_pred = lda_promo_clf.predict(X_test)
        
        print(f"LDA Status Accuracy: {accuracy_score(y_status_test, status_pred):.4f}")
        print(f"LDA Promo Accuracy: {accuracy_score(y_promo_test, promo_pred):.4f}")
        
        # Print discovered topics
        print("\nDiscovered Topics:")
        feature_names = vectorizer.get_feature_names_out()
        for topic_idx, topic in enumerate(lda_model.components_):
            top_words = [feature_names[i] for i in topic.argsort()[-10:][::-1]]
            print(f"Topic {topic_idx}: {', '.join(top_words)}")
        
        # Save models
        os.makedirs(models_dir, exist_ok=True)
        
        with open(f"{models_dir}/lda_model.pkl", 'wb') as f:
            pickle.dump(lda_model, f)
            
        with open(f"{models_dir}/lda_status_clf.pkl", 'wb') as f:
            pickle.dump(lda_status_clf, f)
            
        with open(f"{models_dir}/lda_promo_clf.pkl", 'wb') as f:
            pickle.dump(lda_promo_clf, f)
            
        with open(f"{models_dir}/vectorizer_lda.pkl", 'wb') as f:
            pickle.dump(vectorizer, f)
        
        print("LDA models saved successfully!")
        return lda_model, lda_status_clf, lda_promo_clf, vectorizer
        
    except Exception as e:
        print(f"Error training LDA model: {e}")
        return None, None, None, None

def analyze_conversation_topics(conversation_text, lda_model, vectorizer, top_n=3):
    """
    Analisis topik dalam percakapan menggunakan trained LDA model
    """
    try:
        # Transform text to topic probabilities
        text_vector = vectorizer.transform([conversation_text])
        topic_probs = lda_model.transform(text_vector)[0]
        
        # Get top topics
        top_topics = topic_probs.argsort()[-top_n:][::-1]
        
        result = []
        for topic_idx in top_topics:
            prob = topic_probs[topic_idx]
            if prob > 0.1:  # Only include topics with significant probability
                result.append({
                    'topic_id': int(topic_idx),
                    'probability': float(prob),
                    'description': f'Topic {topic_idx}'
                })
        
        return result
        
    except Exception as e:
        print(f"Error analyzing topics: {e}")
        return []

if __name__ == "__main__":
    # Train all models
    print("Training SVM models...")
    train_svm_model()
    
    print("\nTraining LDA models...")
    train_lda_model(n_topics=8)  # 8 topik untuk customer service
