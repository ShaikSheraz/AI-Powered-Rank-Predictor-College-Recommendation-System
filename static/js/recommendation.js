// Dynamic dropdown functionality for recommendation page
document.addEventListener('DOMContentLoaded', function() {
    const examSelect = document.getElementById('examSelect');
    const categorySelect = document.getElementById('categorySelect');
    const branchSelect = document.getElementById('branchSelect');
    const categoryHelp = document.getElementById('categoryHelp');
    const branchHelp = document.getElementById('branchHelp');

    console.log("🚀 Recommendation page JavaScript loaded");

    // Branch full form mapping
    const branchMapping = {
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
        'CLOUD': 'Cloud Computing'
    };

    // Load categories and branches when exam is selected
    examSelect.addEventListener('change', function() {
        const exam = this.value;
        
        if (!exam) {
            resetDropdowns();
            return;
        }
        
        // Show loading states
        categorySelect.innerHTML = '<option value="">Loading categories...</option>';
        branchSelect.innerHTML = '<option value="">Loading branches...</option>';
        categoryHelp.textContent = 'Loading categories...';
        branchHelp.textContent = 'Loading branches...';
        categoryHelp.style.color = '#6c757d';
        branchHelp.style.color = '#6c757d';
        
        // Load categories and branches
        loadCategoriesByExam(exam);
        loadBranchesByExam(exam);
    });

    function loadCategoriesByExam(exam) {
        fetch(`/get_categories_by_exam?exam=${encodeURIComponent(exam)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                categorySelect.innerHTML = '<option value="">Select Category</option>';
                
                if (data.categories && data.categories.length > 0) {
                    data.categories.forEach(category => {
                        const option = document.createElement('option');
                        option.value = category;
                        option.textContent = category;
                        categorySelect.appendChild(option);
                    });
                    categoryHelp.textContent = `${data.categories.length} categories available`;
                    categoryHelp.style.color = '#28a745';
                    
                    // Restore previously selected value if exists
                    const previousCategory = "{{ request.form.category if request.method == 'POST' }}";
                    if (previousCategory && previousCategory !== 'None') {
                        categorySelect.value = previousCategory;
                    }
                } else {
                    categorySelect.innerHTML = '<option value="">No categories found</option>';
                    categoryHelp.textContent = 'No categories available for this exam';
                    categoryHelp.style.color = '#dc3545';
                }
            })
            .catch(error => {
                console.error('❌ Error loading categories:', error);
                categorySelect.innerHTML = '<option value="">Error loading categories</option>';
                categoryHelp.textContent = 'Error loading categories. Please try again.';
                categoryHelp.style.color = '#dc3545';
            });
    }

    function loadBranchesByExam(exam) {
        fetch(`/get_branches_by_exam?exam=${encodeURIComponent(exam)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                branchSelect.innerHTML = '<option value="">Select Branch</option>';
                
                if (data.branches && data.branches.length > 0) {
                    data.branches.forEach(branch => {
                        const option = document.createElement('option');
                        
                        // Handle different data formats
                        if (typeof branch === 'object' && branch.value && branch.display) {
                            option.value = branch.value;
                            option.textContent = branch.display;
                            option.title = branch.display;
                        } else if (typeof branch === 'string' && branch.includes(' - ')) {
                            // Handle string format with full form
                            const [value, display] = branch.split(' - ');
                            option.value = value.trim();
                            option.textContent = branch;
                            option.title = branch;
                        } else {
                            // Use branch mapping for full form
                            const fullForm = branchMapping[branch] || branch;
                            option.value = branch;
                            option.textContent = `${branch} - ${fullForm}`;
                            option.title = fullForm;
                        }
                        
                        branchSelect.appendChild(option);
                    });
                    branchHelp.textContent = `${data.branches.length} branches available`;
                    branchHelp.style.color = '#28a745';
                    
                    // Restore previously selected value if exists
                    const previousBranch = "{{ request.form.branch if request.method == 'POST' }}";
                    if (previousBranch && previousBranch !== 'None') {
                        branchSelect.value = previousBranch;
                    }
                } else {
                    branchSelect.innerHTML = '<option value="">No branches found</option>';
                    branchHelp.textContent = 'No branches available for this exam';
                    branchHelp.style.color = '#dc3545';
                }
            })
            .catch(error => {
                console.error('❌ Error loading branches:', error);
                branchSelect.innerHTML = '<option value="">Error loading branches</option>';
                branchHelp.textContent = 'Error loading branches. Please try again.';
                branchHelp.style.color = '#dc3545';
            });
    }

    function resetDropdowns() {
        categorySelect.innerHTML = '<option value="">Select exam first</option>';
        branchSelect.innerHTML = '<option value="">Select exam first</option>';
        categoryHelp.textContent = 'Select exam first to see available categories';
        branchHelp.textContent = 'Select exam first to see available branches';
        categoryHelp.style.color = '#6c757d';
        branchHelp.style.color = '#6c757d';
    }

    // Enhanced percentage bars functionality
    function initializePercentageBars() {
        console.log("🎯 Initializing percentage bars...");
        
        const probabilityContainers = document.querySelectorAll('.probability-container');
        
        probabilityContainers.forEach((container, index) => {
            const probabilityFill = container.querySelector('.probability-fill');
            const probabilityBadge = container.querySelector('.probability-badge');
            
            if (!probabilityFill || !probabilityBadge) {
                console.log("❌ Missing probability elements");
                return;
            }
            
            // Get probability from the badge text
            const badgeText = probabilityBadge.textContent;
            const probability = parseInt(badgeText.replace('%', ''));
            
            if (isNaN(probability)) {
                console.log("❌ Invalid probability value:", badgeText);
                return;
            }
            
            console.log(`📊 Setting up probability bar ${index + 1}: ${probability}%`);
            
            // Determine probability level for CSS targeting
            let probabilityLevel = 'very-low';
            if (probability >= 90) probabilityLevel = 'very-high';
            else if (probability >= 80) probabilityLevel = 'high';
            else if (probability >= 60) probabilityLevel = 'medium';
            else if (probability >= 30) probabilityLevel = 'low';
            
            // Set data attribute for CSS targeting
            container.setAttribute('data-probability-level', probabilityLevel);
            
            // Reset width to 0 for animation
            probabilityFill.style.width = '0%';
            
            // Force reflow
            probabilityFill.offsetHeight;
            
            // Animate to target width with staggered delay
            setTimeout(() => {
                probabilityFill.style.transition = `width 1.2s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1}s`;
                probabilityFill.style.width = probability + '%';
                
                console.log(`✅ Animated probability bar ${index + 1} to ${probability}%`);
            }, 100);
        });
    }

    // Enhanced table row animations
    function animateTableRows() {
        const tableRows = document.querySelectorAll('.recommendation-row');
        
        tableRows.forEach((row, index) => {
            // Initial state
            row.style.opacity = '0';
            row.style.transform = 'translateY(30px)';
            row.style.transition = `all 0.6s ease ${index * 0.1}s`;
            
            // Animate in with staggered delay
            setTimeout(() => {
                row.style.opacity = '1';
                row.style.transform = 'translateY(0)';
            }, index * 150 + 200);
        });
    }

    // Enhanced explanation cards with better hover effects
    function initExplanationCards() {
        const explanationCards = document.querySelectorAll('.explanation-card');
        
        explanationCards.forEach(card => {
            card.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            
            card.addEventListener('mouseenter', function() {
                this.style.boxShadow = '0 12px 35px rgba(0,0,0,0.2)';
                this.style.transform = 'translateY(-8px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';
                this.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    // Form submission enhancement
    function enhanceFormSubmission() {
        const form = document.getElementById('recommendationForm');
        
        form.addEventListener('submit', function(e) {
            const rank = document.querySelector('input[name="rank"]').value;
            const exam = document.querySelector('select[name="exam"]').value;
            const category = document.querySelector('select[name="category"]').value;
            const branch = document.querySelector('select[name="branch"]').value;
            
            if (!rank || !exam || !category || !branch) {
                return; // Let HTML5 validation handle it
            }
            
            // Add loading state to button
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            submitBtn.disabled = true;
            
            // Re-enable button after 5 seconds (in case of error)
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 5000);
        });
    }

    // Initialize all animations and effects
    function initializePageEffects() {
        console.log("🎬 Initializing page effects...");
        
        // Initialize with delays to ensure DOM is ready
        setTimeout(() => {
            animateTableRows();
            initExplanationCards();
            initializePercentageBars();
            enhanceFormSubmission();
        }, 300);
    }

    // Auto-initialize if exam is already selected (after form submission)
    if (examSelect && examSelect.value) {
        console.log("📝 Form already submitted, auto-loading dropdowns...");
        examSelect.dispatchEvent(new Event('change'));
    }
    
    // Enhanced initialization for recommendations display
    const recommendationsExist = document.querySelector('.recommendations-results');
    if (recommendationsExist) {
        console.log("📋 Recommendations found, initializing animations...");
        
        // Multiple initialization attempts for reliability
        initializePageEffects();
        setTimeout(initializePageEffects, 800);
        setTimeout(initializePageEffects, 1500);
        
        // Re-initialize on user interaction
        document.addEventListener('click', function() {
            setTimeout(initializePercentageBars, 50);
        });
        
        // Re-initialize on window resize
        window.addEventListener('resize', function() {
            setTimeout(initializePercentageBars, 100);
        });
        
        // Re-initialize when page becomes visible
        document.addEventListener('visibilitychange', function() {
            if (!document.hidden) {
                setTimeout(initializePercentageBars, 200);
            }
        });
    } else {
        // Initialize basic page effects for fresh form
        initializePageEffects();
    }

    // Add smooth scrolling to results
    if (recommendationsExist && !document.querySelector('.alert-warning')) {
        setTimeout(() => {
            recommendationsExist.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 1000);
    }

    console.log("✅ Recommendation page JavaScript initialized successfully");
});

// Utility function for branch full forms (can be used elsewhere)
function getBranchFullForm(branchShort) {
    const branchMapping = {
        'CSE': 'Computer Science and Engineering',
        'CS': 'Computer Science and Engineering',
        'CSIT': 'Computer Science and Information Technology',
        'IT': 'Information Technology',
        'ECE': 'Electronics and Communication Engineering',
        'EEE': 'Electrical and Electronics Engineering',
        'MECH': 'Mechanical Engineering',
        'CIVIL': 'Civil Engineering',
        // ... (same mapping as above)
    };
    return branchMapping[branchShort] || branchShort;
}

