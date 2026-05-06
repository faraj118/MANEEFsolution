// Maneef Sidebar Utilities
// Consolidated shared functions for all sidebar implementations
// Reduces code duplication and provides single source of truth for UI formatting

window.maneef = window.maneef || {};
window.maneef.sidebar = {
    /**
     * Generates a styled sidebar item card
     * @param {string} label - The label text (displayed in small gray text)
     * @param {string} value - The value to display (shown in larger bold text)
     * @param {string} color - Hex color code for the value text
     * @returns {string} HTML string for the sidebar item
     */
    sidebarItem: function(label, value, color) {
        return '<div style="margin-bottom:10px;">' +
            '<div style="font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:2px;">' + label + '</div>' +
            '<div style="font-size:13px;font-weight:600;color:' + color + ';">' + value + '</div>' +
            '</div>';
    },

    /**
     * Maps risk/status ratings to standardized colors
     * @param {string} rating - The rating value (e.g., "Low", "Green", "Critical")
     * @returns {string} Hex color code
     */
    getRiskColor: function(rating) {
        let colors = {
            "Low": "#10b981",
            "Green": "#10b981",
            "Medium": "#f59e0b",
            "Amber": "#f59e0b",
            "High": "#ef4444",
            "Red": "#ef4444",
            "Unacceptable": "#ef4444",
            "Critical": "#ef4444"
        };
        return colors[rating] || "#64748b";
    },

    /**
     * Formats a numeric value as currency using user's default currency
     * @param {number} value - The amount to format
     * @returns {string} Formatted currency string
     */
    formatCurrency: function(value) {
        try {
            const currency = frappe.defaults.get_default("currency") || "USD";
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: currency
            }).format(value);
        } catch (e) {
            return "$" + (value || 0).toFixed(2);
        }
    }
};
