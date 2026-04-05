// Project Charter Sidebar Integration
// This script enhances the Project Charter form with sidebar visibility and quick actions

frappe.ui.form.on('Project Charter', {
    refresh: function(frm) {
        // Add sidebar sections and quick actions
        frm.trigger('setup_sidebar_sections');
        frm.trigger('add_quick_actions');
        
        // Load project summary if project is linked
        if (frm.doc.project) {
            frm.trigger('load_project_summary');
        }
    },

    setup_sidebar_sections: function(frm) {
        // Add sidebar section for Project Overview
        frm.fields_dict.project.sidebar_include = true;
        frm.fields_dict.customer.sidebar_include = true;
        frm.fields_dict.start_date.sidebar_include = true;
        frm.fields_dict.end_date.sidebar_include = true;
        frm.fields_dict.total_budget.sidebar_include = true;
        frm.fields_dict.project_priority.sidebar_include = true;
        frm.fields_dict.risk_level.sidebar_include = true;
    },

    add_quick_actions: function(frm) {
        // Only add buttons for submitted documents
        if (frm.doc.docstatus === 1) {
            // Create/Update Project button
            if (!frm.doc.project) {
                frm.add_custom_button(__('Create Project'), function() {
                    frm.call('create_or_update_project').then(() => {
                        frm.reload_doc();
                        frappe.show_alert({message: __('Project created/updated successfully'), indicator:'green'});
                    });
                }).addClass('btn-primary');
            } else {
                frm.add_custom_button(__('Update Project'), function() {
                    frm.call('create_or_update_project').then(() => {
                        frm.reload_doc();
                        frappe.show_alert({message: __('Project updated successfully'), indicator:'green'});
                    });
                }).addClass('btn-secondary');
            }

            // Generate Tasks from Briefs button
            if (frm.doc.custom_task_briefs && frm.doc.custom_task_briefs.length > 0) {
                frm.add_custom_button(__('Generate Tasks'), function() {
                    frm.call('generate_tasks_from_briefs', {project_name: frm.doc.project}).then(() => {
                        frappe.show_alert({message: __('Tasks generated from briefs'), indicator:'green'});
                    });
                }).addClass('btn-default');
            }

            // View Linked Sales Order button
            if (frm.doc.sales_order) {
                frm.add_custom_button(__('View Sales Order'), function() {
                    frappe.set_route('Form/Sales Order', frm.doc.sales_order);
                }).addClass('btn-default');
            }

            // View Project Dashboard button
            if (frm.doc.project) {
                frm.add_custom_button(__('Project Dashboard'), function() {
                    frappe.set_route('query-report/project_health_matrix', frm.doc.project);
                }).addClass('btn-default');
            }
        }
    },

    load_project_summary: function(frm) {
        frappe.call({
            method: 'maneef.crm_commercial.doctype.project_charter.project_charter.get_project_summary',
            args: {
                project_name: frm.doc.project
            },
            callback: function(r) {
                if (r.message) {
                    // Display project summary in a sidebar panel
                    frm.set_df_property('project', 'description', 
                        `<div class="project-summary-sidebar">
                            <h5>${r.message.project_name}</h5>
                            <p><strong>Status:</strong> <span class="indicator-pill ${r.message.status.toLowerCase()}">${r.message.status}</span></p>
                            <p><strong>Budget:</strong> ${frappe.format(r.message.contracted_fee, {fieldtype: 'Currency'})}</p>
                            <p><strong>Burn:</strong> ${r.message.burn_percentage.toFixed(1)}%</p>
                            <p><strong>Tasks:</strong> ${r.message.completed_tasks}/${r.message.total_tasks} (${r.message.completion_rate.toFixed(1)}%)</p>
                        </div>`
                    );
                }
            }
        });
    },

    // Update project field when project is created
    project: function(frm) {
        // Reload to show new project link and summary
        if (frm.doc.project) {
            frm.trigger('load_project_summary');
        }
    },

    // Recalculate budget breakdown percentages when amounts change
    budget_breakdown: function(frm, cdt, cdn) {
        let child = locals[cdt][cdn];
        if (child.amount && frm.doc.total_budget && frm.doc.total_budget > 0) {
            child.percentage = (child.amount / frm.doc.total_budget * 100);
            frm.refresh_field('budget_breakdown');
        }
    },

    // Auto-calculate total from budget breakdown
    total_budget: function(frm) {
        if (frm.doc.budget_breakdown && frm.doc.budget_breakdown.length > 0) {
            let calculated_total = sum(frm.doc.budget_breakdown, (item) => item.amount || 0);
            if (Math.abs(calculated_total - frm.doc.total_budget) > 0.01) {
                frappe.msgprint({
                    title: __('Budget Mismatch'),
                    message: __('Total budget ({0}) does not match sum of breakdown ({1})', 
                        [frappe.format(frm.doc.total_budget, {fieldtype: 'Currency'}), 
                         frappe.format(calculated_total, {fieldtype: 'Currency'})]),
                    indicator:'orange'
                });
            }
        }
    }
});

// Custom CSS for sidebar styling
$(document).on('form-load', function(e, form) {
    if (form.doctype === 'Project Charter') {
        // Add custom styles for project summary
        let style = `
            <style>
                .project-summary-sidebar {
                    padding: 10px;
                    background: var(--bg-color);
                    border-radius: 4px;
                    margin: -10px;
                }
                .project-summary-sidebar h5 {
                    margin: 0 0 10px 0;
                    color: var(--text-color);
                    font-size: 14px;
                    font-weight: 600;
                }
                .project-summary-sidebar p {
                    margin: 5px 0;
                    font-size: 12px;
                }
                .indicator-pill {
                    display: inline-block;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: 500;
                }
                .indicator-pill.open { background: #e6f4ea; color: #1e7e34; }
                .indicator-pill.working { background: #e3f2fd; color: #1976d2; }
                .indicator-pill.completed { background: #f3e5f5; color: #7b1fa2; }
                .indicator-pill.cancelled { background: #ffebee; color: #c62828; }
            </style>
        `;
        $('head').append(style);
    }
});