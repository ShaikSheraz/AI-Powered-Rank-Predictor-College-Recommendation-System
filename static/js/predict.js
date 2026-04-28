// Step-by-step form functionality
let currentStep = 1;

function nextStep(step) {
    if (step === 1) {
        // Validate step 1
        const rank = document.getElementById('rankInput').value;
        const exam = document.getElementById('examSelect').value;
        
        if (!rank || !exam) {
            alert('Please enter rank and select exam');
            return;
        }
        
        // Load colleges for selected exam
        loadCollegesByExam(exam);
    }
    else if (step === 2) {
        // Validate step 2
        const college = document.getElementById('collegeInput').value;
        if (!college) {
            alert('Please select a college');
            return;
        }
        
        // Load categories for selected college
        const exam = document.getElementById('examSelect').value;
        loadCategoriesByCollege(exam, college);
    }
    
    // Hide current step
    document.getElementById(`step${step}`).classList.remove('active');
    document.getElementById(`step${step}-indicator`).classList.remove('active');
    
    // Show next step
    currentStep = step + 1;
    document.getElementById(`step${currentStep}`).classList.add('active');
    document.getElementById(`step${currentStep}-indicator`).classList.add('active');
}

function prevStep(step) {
    // Clear form data based on which step we're going back from
    if (step === 3) {
        // Clear step 3 data (Category & Branch)
        document.getElementById('categorySelect').innerHTML = '<option value="">Select College First</option>';
        document.getElementById('branchSelect').innerHTML = '<option value="">Select Category First</option>';
        document.getElementById('categoryHelp').textContent = 'Select college to see available categories';
        document.getElementById('branchHelp').textContent = 'Select category to see available branches';
    }
    else if (step === 2) {
        // Clear step 2 data (College)
        document.getElementById('collegeInput').value = '';
        document.getElementById('collegeHelp').textContent = 'Type 2+ characters to see college suggestions';
        closeAllLists();  // Now defined below
        
        // Also clear step 3 data since it depends on college
        document.getElementById('categorySelect').innerHTML = '<option value="">Select College First</option>';
        document.getElementById('branchSelect').innerHTML = '<option value="">Select Category First</option>';
        document.getElementById('categoryHelp').textContent = 'Select college to see available categories';
        document.getElementById('branchHelp').textContent = 'Select category to see available branches';
    }
    
    // Hide current step
    document.getElementById(`step${step}`).classList.remove('active');
    document.getElementById(`step${step}-indicator`).classList.remove('active');
    
    // Show previous step
    currentStep = step - 1;
    document.getElementById(`step${currentStep}`).classList.add('active');
    document.getElementById(`step${currentStep}-indicator`).classList.add('active');
}

function loadCollegesByExam(exam) {
    fetch(`/get_colleges_by_exam?exam=${encodeURIComponent(exam)}`)
        .then(response => response.json())
        .then(data => {
            console.log("📊 Colleges loaded:", data.colleges.length);
            // We don't populate dropdown, but enable search
            document.getElementById('collegeHelp').textContent = 
                `Type to search ${data.colleges.length} colleges`;
        })
        .catch(error => {
            console.error('❌ Error loading colleges:', error);
        });
}

function loadCategoriesByCollege(exam, college) {
    document.getElementById('categorySelect').innerHTML = '<option value="">Loading categories...</option>';
    document.getElementById('branchSelect').innerHTML = '<option value="">Select category first</option>';
    
    fetch(`/get_categories_by_college?exam=${encodeURIComponent(exam)}&college=${encodeURIComponent(college)}`)
        .then(response => response.json())
        .then(data => {
            const categorySelect = document.getElementById('categorySelect');
            categorySelect.innerHTML = '<option value="">Select Category</option>';
            
            if (data.categories && data.categories.length > 0) {
                data.categories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category;
                    option.textContent = category;
                    categorySelect.appendChild(option);
                });
                document.getElementById('categoryHelp').textContent = 
                    `${data.categories.length} categories available`;
            } else {
                categorySelect.innerHTML = '<option value="">No categories found</option>';
                document.getElementById('categoryHelp').textContent = 'No categories available';
            }
        })
        .catch(error => {
            console.error('❌ Error loading categories:', error);
            document.getElementById('categorySelect').innerHTML = '<option value="">Error loading categories</option>';
        });
}

// UTILITY FUNCTIONS - MOVED TO TOP LEVEL TO AVOID SCOPE ISSUES
function closeAllLists() {
    const autocompleteList = document.getElementById('collegeAutocompleteList');
    if (autocompleteList) {
        const items = autocompleteList.getElementsByTagName('div');
        while (items.length > 0) {
            autocompleteList.removeChild(items[0]);
        }
    }
    window.currentFocus = -1;  // Global scope
}

function addActive(items) {
    if (!items) return false;
    removeActive(items);
    
    if (window.currentFocus >= items.length) window.currentFocus = 0;
    if (window.currentFocus < 0) window.currentFocus = items.length - 1;
    
    if (items[window.currentFocus]) {
        items[window.currentFocus].classList.add('autocomplete-active');
    }
}

function removeActive(items) {
    for (let i = 0; i < items.length; i++) {
        items[i].classList.remove('autocomplete-active');
    }
}

// Reset form completely (for new prediction after getting result)
function resetForm() {
    currentStep = 1;
    
    // Reset all steps to initial state
    document.querySelectorAll('.form-step').forEach(step => {
        step.classList.remove('active');
    });
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });
    
    // Show step 1
    document.getElementById('step1').classList.add('active');
    document.getElementById('step1-indicator').classList.add('active');
    
    // Clear all form data
    document.getElementById('rankInput').value = '';
    document.getElementById('examSelect').value = '';
    document.getElementById('collegeInput').value = '';
    document.getElementById('categorySelect').innerHTML = '<option value="">Select College First</option>';
    document.getElementById('branchSelect').innerHTML = '<option value="">Select Category First</option>';
    
    // Reset help text
    document.getElementById('collegeHelp').textContent = 'Type 2+ characters to see college suggestions';
    document.getElementById('categoryHelp').textContent = 'Select college to see available categories';
    document.getElementById('branchHelp').textContent = 'Select category to see available branches';
    
    closeAllLists();
}

// When category changes, load branches
document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.getElementById('categorySelect');
    const branchSelect = document.getElementById('branchSelect');
    const collegeInput = document.getElementById('collegeInput');
    const examSelect = document.getElementById('examSelect');
    const autocompleteList = document.getElementById('collegeAutocompleteList');
    const collegeLoading = document.getElementById('collegeLoading');
    const collegeHelp = document.getElementById('collegeHelp');
    window.currentFocus = -1;  // Global variable
    
    categorySelect.addEventListener('change', function() {
        const exam = examSelect.value;
        const college = collegeInput.value;
        const category = this.value;
        
        if (!exam || !college || !category) return;
        
        branchSelect.innerHTML = '<option value="">Loading branches...</option>';
        
        fetch(`/get_branches_by_college_category?exam=${encodeURIComponent(exam)}&college=${encodeURIComponent(college)}&category=${encodeURIComponent(category)}`)
            .then(response => response.json())
            .then(data => {
                branchSelect.innerHTML = '<option value="">Select Branch</option>';
                
                if (data.branches && data.branches.length > 0) {
                    data.branches.forEach(branch => {
                        const option = document.createElement('option');
                        // Handle both object format and simple array format
                        if (typeof branch === 'object' && branch.value && branch.display) {
                            option.value = branch.value;
                            option.textContent = branch.display;
                        } else if (typeof branch === 'string' && branch.includes(' - ')) {
                            // Handle string format with full form: "CSE - Computer Science and Engineering"
                            const [value, display] = branch.split(' - ');
                            option.value = value.trim();
                            option.textContent = branch;
                        } else {
                            // Fallback: use as-is
                            option.value = branch;
                            option.textContent = branch;
                        }
                        branchSelect.appendChild(option);
                    });
                    document.getElementById('branchHelp').textContent = 
                        `${data.branches.length} branches available`;
                } else {
                    branchSelect.innerHTML = '<option value="">No branches found</option>';
                    document.getElementById('branchHelp').textContent = 'No branches available';
                }
            })
            .catch(error => {
                console.error('❌ Error loading branches:', error);
                branchSelect.innerHTML = '<option value="">Error loading branches</option>';
            });
    });

    // College search functionality - ALL UTILITIES NOW DEFINED
    collegeInput.addEventListener('input', function() {
        const query = this.value.trim();
        const exam = examSelect.value;
        
        if (query.length < 2) {
            closeAllLists();
            collegeHelp.textContent = 'Type 2+ characters to see college suggestions';
            return;
        }
        
        if (!exam) {
            alert('Please select an exam first');
            this.value = '';
            return;
        }
        
        collegeLoading.style.display = 'block';
        collegeHelp.textContent = 'Searching colleges...';
        
        clearTimeout(window.collegeSearchTimeout);
        window.collegeSearchTimeout = setTimeout(() => {
            fetch(`/search_colleges?q=${encodeURIComponent(query)}&exam=${encodeURIComponent(exam)}`)
                .then(response => response.json())
                .then(data => {
                    collegeLoading.style.display = 'none';
                    
                    if (data.colleges && data.colleges.length > 0) {
                        collegeHelp.textContent = `Found ${data.colleges.length} colleges. Click to select.`;
                        showAutocompleteSuggestions(data.colleges, query);
                    } else {
                        collegeHelp.textContent = 'No colleges found. Try a different search.';
                        closeAllLists();
                    }
                })
                .catch(error => {
                    collegeLoading.style.display = 'none';
                    console.error('❌ Error fetching colleges:', error);
                    collegeHelp.textContent = 'Error searching colleges';
                });
        }, 300);
    });

    function showAutocompleteSuggestions(colleges, query) {
        closeAllLists();
        window.currentFocus = -1;
        
        colleges.forEach(college => {
            const item = document.createElement('div');
            
            const highlightedCollege = highlightMatch(college, query);
            item.innerHTML = highlightedCollege;
            item.innerHTML += `<input type='hidden' value='${college}'>`;
            
            item.addEventListener('click', function() {
                collegeInput.value = this.getElementsByTagName('input')[0].value;
                collegeHelp.textContent = `Selected: ${collegeInput.value}`;
                closeAllLists();
                
                // Auto-load categories when college is selected
                const exam = examSelect.value;
                if (exam && collegeInput.value) {
                    loadCategoriesByCollege(exam, collegeInput.value);
                }
            });
            
            autocompleteList.appendChild(item);
        });
    }
    
    function highlightMatch(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    collegeInput.addEventListener('keydown', function(e) {
        const items = autocompleteList.getElementsByTagName('div');
        
        if (e.keyCode === 40) { // Down arrow
            window.currentFocus++;
            addActive(items);
        } else if (e.keyCode === 38) { // Up arrow
            window.currentFocus--;
            addActive(items);
        } else if (e.keyCode === 13) { // Enter
            e.preventDefault();
            if (window.currentFocus > -1 && items[window.currentFocus]) {
                items[window.currentFocus].click();
            }
        } else if (e.keyCode === 27) { // Escape
            closeAllLists();
        }
    });
    
    document.addEventListener('click', function(e) {
        if (e.target !== collegeInput) {
            closeAllLists();
        }
    });

    // Add reset button after prediction result
    const predictionResult = document.querySelector('.prediction-result');
    if (predictionResult) {
        const resetButton = document.createElement('button');
        resetButton.type = 'button';
        resetButton.className = 'btn btn-info mt-3';
        resetButton.innerHTML = '<i class="fas fa-redo"></i> Make New Prediction';
        resetButton.onclick = resetForm;
        predictionResult.appendChild(resetButton);
    }

    // Initialize if exam is already selected (after form submission)
    if (examSelect.value) {
        setTimeout(() => {
            resetForm();
        }, 100);
    }
});
