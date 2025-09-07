function toggleLanguageDropdown() {
    const dropdown = document.getElementById('mobile-language-dropdown');
    dropdown.classList.toggle('hidden');
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function closeDropdown(e) {
        if (!dropdown.contains(e.target) && !e.target.closest('.md\\:hidden button')) {
            dropdown.classList.add('hidden');
            document.removeEventListener('click', closeDropdown);
        }
    });
}

// Close dropdown when a language is selected
document.querySelectorAll('#mobile-language-dropdown button').forEach(button => {
    button.addEventListener('click', () => {
        document.getElementById('mobile-language-dropdown').classList.add('hidden');
    });
});