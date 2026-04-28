from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
import numpy as np
import os
import re
import warnings
from sklearn.exceptions import DataConversionWarning

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
warnings.filterwarnings("ignore", category=DataConversionWarning)

app = Flask(__name__)

# --- Enhanced Branch Mapping with Full Forms ---
BRANCH_MAPPING = {
    'CSE': 'Computer Science and Engineering',
    'CS': 'Computer Science and Engineering',
    'CSIT': 'Computer Science and Information Technology',
    'IT': 'Information Technology',
    'ECE': 'Electronics and Communication Engineering',
    'EEE': 'Electrical and Electronics Engineering',
    'MECH': 'Mechanical Engineering',
    'CIVIL': 'Civil Engineering',
    'AERO': 'Aerospace Engineering',
    'AUTO': 'Automobile Engineering',
    'CHEM': 'Chemical Engineering',
    'BT': 'Biotechnology',
    'BME': 'Biomedical Engineering',
    'EI': 'Electronics and Instrumentation Engineering',
    'EE': 'Electrical Engineering',
    'ECM': 'Electronics and Computer Engineering',
    'EIE': 'Electronics and Instrumentation Engineering',
    'ICE': 'Instrumentation and Control Engineering',
    'PROD': 'Production Engineering',
    'META': 'Metallurgical Engineering',
    'MINING': 'Mining Engineering',
    'AGRI': 'Agricultural Engineering',
    'FOOD': 'Food Technology',
    'TEXTILE': 'Textile Technology',
    'PETRO': 'Petroleum Engineering',
    'MARINE': 'Marine Engineering',
    'NAVAL': 'Naval Architecture',
    'CERAMIC': 'Ceramic Technology',
    'PLASTIC': 'Plastic Technology',
    'PAPER': 'Pulp and Paper Technology',
    'PRINTING': 'Printing Technology',
    'ENVIRO': 'Environmental Engineering',
    'SAFETY': 'Safety and Fire Engineering',
    'CSBS': 'Computer Science and Business Systems',
    'AIML': 'Artificial Intelligence and Machine Learning',
    'DS': 'Data Science',
    'CYBER': 'Cyber Security',
    'IOT': 'Internet of Things',
    'ROBOTICS': 'Robotics Engineering',
    'CLOUD': 'Cloud Computing',
    'CSC': 'Computer Science and Engineering',
    'CAC': 'Computer Science and Engineering',
    'CST': 'Computer Science and Technology',
    'CSD': 'Computer Science and Design',
    'CSN': 'Computer Science and Networking',
    'CSS': 'Computer Science and Systems',
    'ICT': 'Information and Communication Technology',
    'BCA': 'Bachelor of Computer Applications',
    'MCA': 'Master of Computer Applications'
}

def get_branch_full_form(branch_short):
    """Get full form of branch names with enhanced mapping"""
    return BRANCH_MAPPING.get(branch_short.upper(), branch_short)

def get_branch_display_name(branch_short):
    """Get display name for dropdown (short - full form)"""
    full_form = get_branch_full_form(branch_short)
    if full_form != branch_short:
        return f"{branch_short} - {full_form}"
    return branch_short

def normalize_text(text):
    """Normalize text for comparison by keeping only letters and digits."""
    if text is None:
        return ''
    return re.sub(r'[^A-Z0-9]', '', str(text).upper())

def normalize_college_name(college_name):
    """Normalize college names for matching across hyphens/spaces/punctuation."""
    if college_name is None or pd.isna(college_name):
        return ''
    return normalize_text(college_name)

def normalize_branch(branch_label):
    """Normalize branch labels to canonical branch codes."""
    if branch_label is None:
        return ''
    raw = str(branch_label).strip()
    if raw == '':
        return ''

    label = raw.upper().strip()

    # If the branch already contains a known code at the start, use that code.
    if ' - ' in label:
        prefix = label.split(' - ', 1)[0].strip()
        if prefix in BRANCH_MAPPING:
            return prefix
    if '-' in label and ' - ' not in label:
        prefix = label.split('-', 1)[0].strip()
        if prefix in BRANCH_MAPPING:
            return prefix

    # Exact code values
    if label in BRANCH_MAPPING:
        return label

    normalized = normalize_text(label)

    # Exact mapping via full form or known short codes
    reverse_map = {normalize_text(k): k for k in BRANCH_MAPPING.keys()}
    reverse_map_full = {}
    for k, v in BRANCH_MAPPING.items():
        key = normalize_text(v)
        if key not in reverse_map_full:
            reverse_map_full[key] = k
        # Prefer canonical CSE for the Computer Science and Engineering full form
        if key == normalize_text('Computer Science and Engineering'):
            reverse_map_full[key] = 'CSE'

    if normalized in reverse_map:
        return reverse_map[normalized]
    if normalized in reverse_map_full:
        return reverse_map_full[normalized]

    # Try to match any candidate segment separated by punctuation
    for candidate in re.split(r'[\s\-\/&]+', label):
        cand_norm = normalize_text(candidate)
        if cand_norm in reverse_map:
            return reverse_map[cand_norm]
        if cand_norm in reverse_map_full:
            return reverse_map_full[cand_norm]

    # Fallback heuristics for common branch names
    if 'COMPUTERSCIENCE' in normalized and 'ENGINEER' in normalized:
        return 'CSE'
    if 'ELECTRONICS' in normalized and 'COMMUNICATION' in normalized:
        return 'ECE'
    if 'ELECTRICAL' in normalized and 'ELECTRONICS' in normalized:
        return 'EEE'
    if 'MECHANICAL' in normalized:
        return 'MECH'
    if 'INFORMATIONTECHNOLOGY' in normalized or 'INFORMATIONANDCOMMUNICATIONTECHNOLOGY' in normalized:
        return 'IT'

    return raw

# --- Helper Functions ---
def get_college_abbreviation(college_name):
    """Generate abbreviation from college name (first letters of each word)"""
    words = str(college_name).upper().split()
    abbreviation = ''.join(word[0] for word in words if word and word[0].isalpha())
    return abbreviation

def clean_category_data(df):
    """Prepare category data - KEEP ALL categories (user requested to keep all)"""
    if len(df) == 0:
        return df
    
    print("🧹 Preparing category data...")
    
    # Remove rows with missing or invalid categories
    df_clean = df.dropna(subset=['category'])
    df_clean = df_clean[df_clean['category'].str.strip() != '']
    
    print(f"✅ Keeping all {len(df_clean)} category records (including ESTD, years, etc.)")
    
    return df_clean

def calculate_mean_cutoffs(df):
    """Calculate mean cutoffs for colleges with multiple years of data - FIXED GATE PROCESSING"""
    if len(df) == 0:
        return pd.DataFrame()
    
    print("📊 Calculating mean cutoffs...")
    
    # Remove rows with missing categories, branches, or invalid cutoffs
    df_clean = df.dropna(subset=['category', 'branch', 'cutoff'])
    df_clean = df_clean[df_clean['category'].str.strip() != '']
    df_clean = df_clean[df_clean['branch'].str.strip() != '']
    df_clean = df_clean[df_clean['cutoff'] > 0]
    
    print(f"🔧 Removed {len(df) - len(df_clean)} invalid records")
    
    # Clean category data to remove ESTD, years, etc.
    df_clean = clean_category_data(df_clean)
    
    # SPECIAL HANDLING FOR JEE DATA
    jee_data = df_clean[df_clean['exam'] == 'JEE']
    other_data = df_clean[df_clean['exam'] != 'JEE']
    
    print(f"🔍 JEE records before processing: {len(jee_data)}")
    
    # For JEE: Use closing rank directly (no mean calculation needed for single year data)
    # But if there are multiple years, we need to handle them properly
    jee_processed = jee_data.copy()
    
    # Check if JEE data has multiple entries for same college+branch+category
    jee_duplicates = jee_processed.duplicated(subset=['college', 'branch', 'category'], keep=False)
    
    if jee_duplicates.any():
        print("⚠️  Found duplicate JEE entries. Processing...")
        # Group and take the minimum cutoff (most recent or most relevant)
        jee_processed = jee_processed.groupby(['exam', 'college', 'branch', 'category']).agg({
            'cutoff': 'min'  # Take the minimum (most competitive) cutoff
        }).reset_index()
        print(f"✅ GATE records after deduplication: {len(jee_processed)}")
    
    # For AP/TS: Calculate mean of multiple years
    if len(other_data) > 0:
        other_processed = other_data.groupby(['exam', 'college', 'branch', 'category'])['cutoff'].mean().reset_index()
    else:
        other_processed = pd.DataFrame()
    
    # Combine JEE and other data
    if len(jee_processed) > 0 and len(other_processed) > 0:
        mean_cutoffs = pd.concat([jee_processed, other_processed], ignore_index=True)
    elif len(jee_processed) > 0:
        mean_cutoffs = jee_processed
    else:
        mean_cutoffs = other_processed
    
    # Log detailed statistics for debugging
    print("📈 Cutoff Statistics by Exam:")
    for exam in ['AP', 'TS', 'JEE']:
        exam_data = mean_cutoffs[mean_cutoffs['exam'] == exam]
        if len(exam_data) > 0:
            cutoff_stats = exam_data['cutoff'].describe()
            print(f"   {exam}: {len(exam_data)} records")
            print(f"      Min: {cutoff_stats['min']:.0f}, Max: {cutoff_stats['max']:.0f}, Mean: {cutoff_stats['mean']:.0f}")
            
            # Show sample categories for debugging
            sample_categories = exam_data['category'].unique()[:5]
            print(f"      Sample categories: {', '.join(sample_categories)}")
    
    print(f"✅ Final mean cutoffs: {len(mean_cutoffs)} records")
    return mean_cutoffs

def standardize_category(cat):
    """Standardize category names - INCLUDING JEE CATEGORIES"""
    if pd.isna(cat) or not isinstance(cat, str):
        return "UNKNOWN"
    
    cat = str(cat).upper().strip()
    
    # Skip if it looks like ESTD or year
    if (cat in ['ESTD', 'ESTD.', 'ESTABLISHED', 'YEAR', 'EST'] or
        cat.isdigit() and len(cat) == 4):  # Year like 1990, 2000
        return "INVALID"
    
    # JEE Categories
    if 'OPEN' in cat: return 'OPEN'
    if 'OBC' in cat and 'NCL' in cat: return 'OBC-NCL'
    if 'OBC' in cat: return 'OBC'
    if 'SC' in cat: return 'SC'
    if 'ST' in cat: return 'ST'
    if 'EWS' in cat: return 'EWS'
    if 'GENERAL' in cat: return 'GENERAL'
    
    # AP/TS Categories
    if 'OC' in cat and 'BOYS' in cat: return 'OC_BOYS'
    if 'OC' in cat and 'GIRLS' in cat: return 'OC_GIRLS'
    if 'SC' in cat and 'BOYS' in cat: return 'SC_BOYS'
    if 'SC' in cat and 'GIRLS' in cat: return 'SC_GIRLS'
    if 'ST' in cat and 'BOYS' in cat: return 'ST_BOYS'
    if 'ST' in cat and 'GIRLS' in cat: return 'ST_GIRLS'
    if 'BC' in cat or 'OBC' in cat:
        if 'BOYS' in cat: return 'BC_BOYS'
        if 'GIRLS' in cat: return 'BC_GIRLS'
        return 'BC'
    if 'EWS' in cat: return 'EWS'
    
    return cat

def is_valid_category(cat):
    """Check if category is valid (not ESTD, year, etc.)"""
    if pd.isna(cat) or not isinstance(cat, str):
        return False
    
    cat = str(cat).upper().strip()
    
    # Invalid patterns
    invalid_patterns = [
        'ESTD', 'ESTD.', 'ESTABLISHED', 'YEAR', 'EST',
        'NA', 'N/A', 'NULL', 'NONE', 'NOT AVAILABLE',
        'UNKNOWN', 'OTHER', 'MISC', 'MISCELLANEOUS'
    ]
    
    # Check for years (4-digit numbers)
    if cat.isdigit() and len(cat) == 4:
        return False
    
    # Check for dates
    if '/' in cat and any(part.isdigit() for part in cat.split('/')):
        return False
    
    return cat not in invalid_patterns and len(cat) >= 2


def normalize_exam(exam):
    """Normalize exam names so GATE maps to the JEE dataset."""
    if not exam or not isinstance(exam, str):
        return ''
    exam_norm = exam.strip().upper()
    if exam_norm == 'GATE':
        return 'JEE'
    return exam_norm


def normalize_encoder_label(label, encoder):
    """Match a user label to an encoder class value case-insensitively."""
    if label is None or not isinstance(label, str):
        return label
    label = label.strip()
    if label in encoder.classes_:
        return label
    upper_label = label.upper()
    for cls in encoder.classes_:
        if isinstance(cls, str) and cls.upper() == upper_label:
            return cls
    lower_label = label.lower()
    for cls in encoder.classes_:
        if isinstance(cls, str) and cls.lower() == lower_label:
            return cls
    return label

# --- Load models and data ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    print("🔄 Loading models and data...")
    best_model = joblib.load(os.path.join(BASE_DIR, 'outputs/best_admission_model.joblib'))
    le_exam = joblib.load(os.path.join(BASE_DIR, 'outputs/le_exam.joblib'))
    le_cat = joblib.load(os.path.join(BASE_DIR, 'outputs/le_cat.joblib')) 
    le_branch = joblib.load(os.path.join(BASE_DIR, 'outputs/le_branch.joblib'))
    le_college = joblib.load(os.path.join(BASE_DIR, 'outputs/le_college.joblib'))
    scaler = joblib.load(os.path.join(BASE_DIR, 'outputs/scaler.joblib'))
    
    # Load cleaned cutoffs and normalize branch labels
    cutoffs_df = pd.read_csv(os.path.join(BASE_DIR, 'outputs/cutoffs_cleaned.csv'))
    cutoffs_df['branch'] = cutoffs_df['branch'].fillna('').astype(str).apply(normalize_branch)
    print(f"✅ Loaded cutoffs: {len(cutoffs_df)} records")
    
    # Debug: Check category data before processing
    print("🔍 Checking category data before processing:")
    category_sample = cutoffs_df['category'].dropna().unique()[:10]
    print(f"   Sample categories: {category_sample}")
    
    # Check for ESTD in categories
    estd_categories = cutoffs_df[cutoffs_df['category'].str.upper().str.contains('ESTD', na=False)]
    if len(estd_categories) > 0:
        print(f"⚠️  Found {len(estd_categories)} records with ESTD in category")
        print(f"   Sample ESTD records: {estd_categories[['college', 'category']].head(3).to_dict('records')}")
    
    # Pre-calculate mean cutoffs for colleges with multiple years
    cutoffs_with_mean = calculate_mean_cutoffs(cutoffs_df)
    if len(cutoffs_with_mean) > 0:
        cutoffs_with_mean['college_norm'] = cutoffs_with_mean['college'].astype(str).apply(normalize_college_name)
    
    # Debug: Check categories after processing
    print("🔍 Checking category data after processing:")
    if len(cutoffs_with_mean) > 0:
        final_categories = cutoffs_with_mean['category'].unique()
        print(f"   Final unique categories: {len(final_categories)}")
        print(f"   Sample final categories: {list(final_categories)[:10]}")
    
    print("✅ All models and data loaded successfully")
    
except Exception as e:
    print(f"❌ Error loading models: {e}")
    # Create dummy objects to prevent crashes
    cutoffs_df = pd.DataFrame()
    cutoffs_with_mean = pd.DataFrame()
    best_model = None
    le_exam = le_cat = le_branch = le_college = scaler = None

# --- API Endpoints ---
@app.route('/get_colleges_by_exam')
def get_colleges_by_exam():
    """Get all colleges for selected exam - EXACT NAMES ONLY"""
    exam = normalize_exam(request.args.get('exam', ''))
    
    if not exam or exam not in ['AP', 'TS', 'JEE']:
        return jsonify({'colleges': []})
    
    if len(cutoffs_with_mean) == 0:
        return jsonify({'colleges': []})
    
    try:
        # Get unique colleges for this exam - EXACT NAMES
        exam_data = cutoffs_with_mean[cutoffs_with_mean['exam'] == exam]
        exam_colleges = exam_data['college'].unique()
        colleges = sorted(exam_colleges.tolist())
        
        print(f"📊 {exam}: Found {len(colleges)} unique colleges")
        
        return jsonify({'colleges': colleges})
        
    except Exception as e:
        print(f"❌ Error in get_colleges_by_exam: {e}")
        return jsonify({'colleges': []})

@app.route('/get_categories_by_college')
def get_categories_by_college():
    """Get ALL available categories for selected college and exam - NO FILTERING"""
    college = request.args.get('college', '').strip().upper()
    exam = normalize_exam(request.args.get('exam', ''))
    
    if not college or not exam:
        return jsonify({'categories': []})
    
    if len(cutoffs_with_mean) == 0:
        return jsonify({'categories': []})
    
    try:
        college_norm = normalize_college_name(college)
        # Filter categories for this college and exam - KEEP ALL
        category_data = cutoffs_with_mean[
            (cutoffs_with_mean['college_norm'] == college_norm) &
            (cutoffs_with_mean['exam'] == exam)
        ]
        
        # GET ALL CATEGORIES - don't filter
        all_categories = sorted([str(cat).strip() for cat in category_data['category'].unique() if pd.notna(cat)])
        
        print(f"✅ Found {len(all_categories)} TOTAL categories for {college}:")
        print(f"   Categories: {', '.join(all_categories[:10])}{'...' if len(all_categories) > 10 else ''}")
        
        return jsonify({'categories': all_categories})
        
    except Exception as e:
        print(f"❌ Error in get_categories_by_college: {e}")
        return jsonify({'categories': []})

@app.route('/get_branches_by_college_category')
def get_branches_by_college_category():
    """Get available branches for selected college, exam and category - WITH FULL FORMS"""
    college = request.args.get('college', '').strip().upper()
    exam = normalize_exam(request.args.get('exam', ''))
    category = request.args.get('category', '').strip().upper()
    
    if not college or not exam or not category:
        return jsonify({'branches': []})
    
    if len(cutoffs_with_mean) == 0:
        return jsonify({'branches': []})
    
    try:
        college_norm = normalize_college_name(college)
        # Filter branches for this combination
        branch_data = cutoffs_with_mean[
            (cutoffs_with_mean['college_norm'] == college_norm) &
            (cutoffs_with_mean['exam'] == exam) &
            (cutoffs_with_mean['category'].str.upper() == category)
        ]
        
        branches_short = sorted(branch_data['branch'].unique().tolist())
        
        # Filter out empty branches and create display names with full forms
        branches = []
        for branch_short in branches_short:
            if branch_short and str(branch_short).strip() != '':
                display_name = get_branch_display_name(branch_short)
                branches.append({'value': branch_short, 'display': display_name})
        
        print(f"🔧 Found {len(branches)} branches for {college} - {category}")
        
        return jsonify({'branches': branches})
        
    except Exception as e:
        print(f"❌ Error in get_branches_by_college_category: {e}")
        return jsonify({'branches': []})

@app.route('/get_categories_by_exam')
def get_categories_by_exam():
    """Get all categories for selected exam (for recommendation page) - FILTERED"""
    exam = normalize_exam(request.args.get('exam', ''))
    
    if not exam or exam not in ['AP', 'TS', 'JEE']:
        return jsonify({'categories': []})
    
    if len(cutoffs_with_mean) == 0:
        return jsonify({'categories': []})
    
    try:
        # Get unique categories for this exam
        exam_data = cutoffs_with_mean[cutoffs_with_mean['exam'] == exam]
        
        # Filter out invalid categories
        valid_categories = []
        for cat in exam_data['category'].unique():
            if is_valid_category(cat):
                valid_categories.append(cat)
        
        categories = sorted(valid_categories)
        
        print(f"📊 {exam}: Found {len(categories)} valid categories")
        
        return jsonify({'categories': categories})
        
    except Exception as e:
        print(f"❌ Error in get_categories_by_exam: {e}")
        return jsonify({'categories': []})

@app.route('/get_branches_by_exam')
def get_branches_by_exam():
    """Get all branches for selected exam (for recommendation page) - WITH FULL FORMS"""
    exam = normalize_exam(request.args.get('exam', ''))
    
    if not exam or exam not in ['AP', 'TS', 'JEE']:
        return jsonify({'branches': []})
    
    if len(cutoffs_with_mean) == 0:
        return jsonify({'branches': []})
    
    try:
        # Get unique branches for this exam
        exam_data = cutoffs_with_mean[cutoffs_with_mean['exam'] == exam]
        branches_short = sorted(exam_data['branch'].unique().tolist())
        
        # Filter out empty branches and create display names with full forms
        branches = []
        for branch_short in branches_short:
            if branch_short and str(branch_short).strip() != '':
                display_name = get_branch_display_name(branch_short)
                branches.append({'value': branch_short, 'display': display_name})
        
        print(f"📊 {exam}: Found {len(branches)} branches")
        
        return jsonify({'branches': branches})
        
    except Exception as e:
        print(f"❌ Error in get_branches_by_exam: {e}")
        return jsonify({'branches': []})

# --- Other routes remain the same ---
@app.route('/search_colleges')
def search_colleges():
    """API endpoint for college name autocomplete - filtered by exam with exact names"""
    query = request.args.get('q', '').strip().upper()
    exam = normalize_exam(request.args.get('exam', ''))
    
    if not query or len(query) < 2:
        return jsonify({'colleges': []})
    
    if len(cutoffs_with_mean) == 0:
        return jsonify({'colleges': []})
    
    try:
        # Filter colleges by exam first
        if exam:
            exam_data = cutoffs_with_mean[cutoffs_with_mean['exam'] == exam]
            exam_colleges = exam_data['college'].unique()
        else:
            exam_colleges = cutoffs_with_mean['college'].unique()
        
        print(f"🔍 Searching {len(exam_colleges)} colleges for exam: {exam}")
        
        # Filter colleges using normalized matching against the user query
        matching_colleges = []
        query_norm = normalize_text(query)
        
        for college in exam_colleges:
            college_upper = str(college).upper()
            college_norm = normalize_text(college_upper)
            
            if (query in college_upper or
                college_upper.startswith(query) or
                any(word.startswith(query) for word in college_upper.split()) or
                (query_norm and query_norm in college_norm)):
                matching_colleges.append(college)
        
        # Remove duplicates and limit results
        unique_colleges = list(set(matching_colleges))[:15]
        
        print(f"🔍 Found {len(unique_colleges)} unique colleges matching '{query}'")
        
        return jsonify({'colleges': sorted(unique_colleges)})
        
    except Exception as e:
        print(f"❌ Error in search_colleges: {e}")
        return jsonify({'colleges': []})

# --- Debug endpoint to check categories ---
@app.route('/debug_categories')
def debug_categories():
    """Debug endpoint to check category data"""
    exam = normalize_exam(request.args.get('exam', 'JEE'))
    
    if len(cutoffs_with_mean) == 0:
        return jsonify({'error': 'No data loaded'})
    
    exam_data = cutoffs_with_mean[cutoffs_with_mean['exam'] == exam]
    
    result = {
        'exam': exam,
        'total_records': len(exam_data),
        'unique_categories': exam_data['category'].unique().tolist(),
        'category_counts': exam_data['category'].value_counts().to_dict(),
        'sample_data': exam_data[['college', 'branch', 'category', 'cutoff']].head(10).to_dict('records')
    }
    
    return jsonify(result)

# --- Prediction and recommendation functions remain the same ---
def predict_admission(rank, exam, category, branch, college):
    """Predict admission probability using XGBoost model"""

    # Normalize inputs
    exam = normalize_exam(exam)
    category = category.strip().upper()
    branch_raw = branch.strip()
    college_input = college.strip().upper()

    # Standardize category name
    category = standardize_category(category)

    # Normalize branch label against encoder classes
    branch = normalize_encoder_label(branch_raw, le_branch)

    print(f"🎯 XGBoost Prediction request: Rank={rank}, Exam={exam}, Category={category}, Branch={branch}, College={college_input}")

    branch_upper = branch_raw.upper()
    # Find exact match with mean cutoffs
    cutoff_data = cutoffs_with_mean[
        (cutoffs_with_mean['exam'] == exam) &
        (cutoffs_with_mean['college'].str.upper() == college_input) &
        (cutoffs_with_mean['branch'].str.upper() == branch_upper) &
        (cutoffs_with_mean['category'].str.upper() == category)
    ]

    if len(cutoff_data) == 0:
        print(f"❌ No cutoff data found for {exam}, {college_input}, {branch}, {category}")
        return {
            'error': f'No cutoff data found for {college}, {branch}, {category}. Please check your selections.',
            'admit': 0,
            'probability': 0,
            'data_quality': 'no_data'
        }

    # Use the mean cutoff
    cutoff = cutoff_data['cutoff'].values[0]
    found_college_name = cutoff_data['college'].values[0]

    print(f"📊 Found cutoff: {cutoff} for college: {found_college_name}")

    # Calculate rank_ratio (needed for XGBoost features)
    rank_ratio = rank / cutoff
    xgboost_used = False  # Track if XGBoost was successfully used

    try:
        # Encode categorical features using trained label encoders
        exam_encoded = le_exam.transform([exam])[0]
        category_encoded = le_cat.transform([category])[0]
        branch_encoded = le_branch.transform([branch])[0]
        college_encoded = le_college.transform([found_college_name])[0]  # Use found name for consistency

        # Create feature vector
        features = [[rank_ratio, exam_encoded, category_encoded, branch_encoded, college_encoded]]

        # Scale features using trained scaler
        features_scaled = scaler.transform(features)

        # XGBoost prediction
        probability = best_model.predict_proba(features_scaled)[0][1] * 100  # Convert to percentage

        # Ensure probability is within bounds
        probability = max(1, min(99, probability))
        admit = 1 if probability >= 50 else 0

        print(f"🤖 XGBoost prediction: {probability:.2f}% (Rank ratio: {rank_ratio:.3f})")
        xgboost_used = True  # Mark that XGBoost was successfully used

    except Exception as e:
        print(f"❌ XGBoost prediction error: {e}")
        # Fallback to rule-based calculation
        print("🔄 Falling back to rule-based calculation")

        if rank <= cutoff:
            if rank <= cutoff * 0.5:
                probability = 98
            elif rank <= cutoff * 0.8:
                probability = 95
            else:
                probability = 85 + ((cutoff - rank) / cutoff * 10)
        else:
            if rank <= cutoff * 1.2:
                probability = 60 - ((rank - cutoff) / cutoff * 20)
            elif rank <= cutoff * 1.5:
                probability = 30 - ((rank - cutoff) / cutoff * 15)
            else:
                probability = 5

        probability = max(1, min(99, probability))
        admit = 1 if probability >= 50 else 0

    result = {
        'admit': admit,
        'probability': round(probability, 2),
        'cutoff_found': round(cutoff, 2),
        'rank_ratio': round(rank_ratio, 2),
        'college_used': found_college_name,
        'message': f"{'Very High' if probability >= 95 else 'High' if probability >= 80 else 'Good' if probability >= 60 else 'Low' if probability >= 30 else 'Very Low'} chance of admission",
        'data_quality': 'xgboost_ml' if xgboost_used else 'rule_based'
    }

    print(f"✅ Prediction successful: {probability}% chance (Rank: {rank}, Cutoff: {cutoff})")
    return result

def recommend_colleges_improved(rank, exam, category, branch, top_n=10):
    """Recommend colleges using XGBoost predictions"""

    exam = normalize_exam(exam)
    branch_raw = branch.strip()
    category = standardize_category(category.strip().upper())
    branch_upper = branch_raw.upper()

    print(f"🎯 XGBoost Recommendation request: Rank={rank}, Exam={exam}, Category={category}, Branch={branch_raw}")

    # Filter colleges for the specific exam, branch, and category
    eligible_colleges = cutoffs_with_mean[
        (cutoffs_with_mean['exam'] == exam) &
        (cutoffs_with_mean['branch'].str.upper() == branch_upper) &
        (cutoffs_with_mean['category'].str.upper() == category)
    ]

    print(f"📊 Found {len(eligible_colleges)} eligible colleges")

    if len(eligible_colleges) == 0:
        return [{'error': f'No colleges found for {exam}, {branch}, {category}'}]

    recommendations = []

    # Pre-encode common features (same for all colleges)
    try:
        exam_encoded = le_exam.transform([exam])[0]
        category_encoded = le_cat.transform([category])[0]
        normalized_branch = normalize_encoder_label(branch_raw, le_branch)
        branch_encoded = le_branch.transform([normalized_branch])[0]
    except Exception as e:
        print(f"❌ Encoding error: {e}")
        return [{'error': f'Feature encoding error: {str(e)}'}]

    for _, row in eligible_colleges.iterrows():
        college = row['college']
        cutoff = row['cutoff']

        # Skip if cutoff is invalid
        if cutoff <= 0 or pd.isna(cutoff):
            continue

        # Calculate rank difference
        rank_difference = cutoff - rank
        rank_ratio = rank / cutoff

        try:
            # Encode college
            college_encoded = le_college.transform([college])[0]

            # Create feature vector
            features = [[rank_ratio, exam_encoded, category_encoded, branch_encoded, college_encoded]]

            # Scale features
            features_scaled = scaler.transform(features)

            # XGBoost prediction
            probability = best_model.predict_proba(features_scaled)[0][1] * 100

            # Ensure probability is within bounds
            probability = max(1, min(99, probability))

        except Exception as e:
            print(f"⚠️ XGBoost prediction failed for {college}: {e}")
            # Fallback to rule-based calculation
            if rank <= cutoff:
                if rank <= cutoff * 0.5:
                    probability = 98
                elif rank <= cutoff * 0.8:
                    probability = 95
                else:
                    probability = 85 + ((cutoff - rank) / cutoff * 10)
            else:
                if rank <= cutoff * 1.2:
                    probability = 60 - ((rank - cutoff) / cutoff * 20)
                elif rank <= cutoff * 1.5:
                    probability = 30 - ((rank - cutoff) / cutoff * 15)
                else:
                    probability = 5
            probability = max(1, min(99, probability))

        # Determine category type based on probability (XGBoost-driven)
        if probability >= 95:
            category_type = 'Very Safe'
        elif probability >= 85:
            category_type = 'Safe Bet'
        elif probability >= 70:
            category_type = 'Good Match'
        elif probability >= 50:
            category_type = 'Ambitious'
        elif probability >= 25:
            category_type = 'Very Ambitious'
        else:
            category_type = 'Highly Ambitious'

        recommendations.append({
            'college': college,
            'probability': round(probability, 2),
            'cutoff': round(cutoff, 2),
            'rank_difference': int(rank_difference),
            'category': category_type
        })

    # Sort by how close the cutoff is to student's rank (maintains rank-based ordering)
    recommendations.sort(key=lambda x: abs(x['cutoff'] - rank))

    print(f"✅ Generated {len(recommendations)} XGBoost-powered recommendations")
    return recommendations[:top_n]

# --- Main Routes ---
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    result = None
    if request.method == 'POST':
        try:
            print("📝 Form submitted to /predict")
            rank = int(request.form['rank'])
            exam = request.form['exam'].strip().upper()
            category = request.form['category'].strip().upper()
            branch = request.form['branch'].strip()
            college = request.form['college'].strip().upper()
            
            print(f"📊 Form data - Rank: {rank}, Exam: {exam}, Category: {category}, Branch: {branch}, College: {college}")
            
            # Input validation
            if rank <= 0:
                result = {'error': 'Rank must be a positive number'}
            elif not exam or not category or not branch or not college:
                result = {'error': 'All fields are required'}
            elif exam not in ['AP', 'TS', 'JEE']:
                result = {'error': 'Exam must be AP, TS, or JEE'}
            else:
                result = predict_admission(rank, exam, category, branch, college)
                
        except ValueError as e:
            print(f"❌ ValueError in predict: {e}")
            result = {'error': 'Rank must be a valid number'}
        except Exception as e:
            print(f"❌ Exception in predict: {e}")
            result = {'error': f'Input error: {str(e)}'}
    
    return render_template('predict.html', result=result)

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    recommendations = []
    if request.method == 'POST':
        try:
            print("📝 Form submitted to /recommend")
            rank = int(request.form['rank'])
            exam = request.form['exam'].strip().upper()
            category = request.form['category'].strip().upper()
            branch = request.form['branch'].strip().upper()
            
            print(f"📊 Form data - Rank: {rank}, Exam: {exam}, Category: {category}, Branch: {branch}")
            
            # Input validation
            if rank <= 0:
                recommendations = [{'error': 'Rank must be a positive number'}]
            elif not exam or not category or not branch:
                recommendations = [{'error': 'All fields are required'}]
            elif exam not in ['AP', 'TS', 'JEE']:
                recommendations = [{'error': 'Exam must be AP, TS, or JEE'}]
            else:
                recommendations = recommend_colleges_improved(rank, exam, category, branch, top_n=10)
                
        except ValueError as e:
            print(f"❌ ValueError in recommend: {e}")
            recommendations = [{'error': 'Rank must be a valid number'}]
        except Exception as e:
            print(f"❌ Exception in recommend: {e}")
            recommendations = [{'error': f'Input error: {str(e)}'}]
    
    print(f"✅ Sending {len(recommendations)} recommendations to template")
    return render_template('recommendation.html', recommendations=recommendations)

if __name__ == '__main__':
    print("🚀 College Admission Predictor Started!")
    print("📊 Available Exams: AP, TS, JEE")
    print("🤖 ML Model: XGBoost (96.87% ROC-AUC)")
    print("🔧 Features:")
    print("   - Enhanced category filtering (removes ESTD, years, etc.)")
    print("   - XGBoost-powered predictions & recommendations")
    print("   - Fixed JEE cutoff processing")
    print("   - JEE Categories: OPEN, OBC-NCL, SC, ST, EWS")
    print("   - Cleaned data (removed invalid records)")
    print("   - Dynamic dropdowns with branch full forms")
    print("🔍 Debug URLs:")
    print("   - /debug_categories?exam=JEE")
    print("   - /debug_jee_college?college=IIT DELHI")
    app.run(debug=True, host='0.0.0.0', port=5000)