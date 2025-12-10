/** @odoo-module **/

import { SearchPanel } from "@web/search/search_panel/search_panel";
import { patch } from "@web/core/utils/patch";
import { Component, useState } from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DateTimePicker } from "@web/core/datetime/datetime_picker";

const { DateTime } = luxon;

// List of models that should have the date range filter
const MODELS_WITH_DATE_FILTER = ["jewelry.client.purchase"];

/**
 * DateRangeFilter Component
 * Provides a two-click date range selection using Odoo's native DateTimePicker
 */
export class DateRangeFilter extends Component {
    static template = "jewelry_purchase_client.DateRangeFilter";
    static components = { Dropdown, DateTimePicker };
    static props = {
        searchModel: Object,
        fieldName: { type: String, optional: true },
        fieldLabel: { type: String, optional: true },
    };

    setup() {
        this.state = useState({
            startDate: false,
            endDate: false,
            focusedDateIndex: 0,  // 0 = selecting start, 1 = selecting end
            isOpen: false,
        });
        this.fieldName = this.props.fieldName || "date";
        this.fieldLabel = this.props.fieldLabel || "Fecha";
    }

    get hasSelection() {
        return this.state.startDate && this.state.endDate;
    }

    get formattedStart() {
        return this.state.startDate ? this.state.startDate.toFormat("dd/MM/yyyy") : "";
    }

    get formattedEnd() {
        return this.state.endDate ? this.state.endDate.toFormat("dd/MM/yyyy") : "";
    }

    get formattedRange() {
        if (!this.hasSelection) {
            return "Seleccionar fechas...";
        }
        return `${this.formattedStart} - ${this.formattedEnd}`;
    }

    get pickerProps() {
        return {
            type: "date",
            range: true,
            value: [this.state.startDate || DateTime.now(), this.state.endDate || DateTime.now()],
            focusedDateIndex: this.state.focusedDateIndex,
            onSelect: this.onDateSelect.bind(this),
        };
    }

    get hintText() {
        if (this.state.focusedDateIndex === 0) {
            return "Selecciona la fecha de inicio";
        }
        return "Selecciona la fecha de fin";
    }

    onDateSelect(value) {
        if (this.state.focusedDateIndex === 0) {
            // First click: set start date
            this.state.startDate = value[0];
            this.state.endDate = false;
            this.state.focusedDateIndex = 1;
        } else {
            // Second click: set end date
            let start = this.state.startDate;
            let end = value[1] || value[0];

            // Ensure start <= end
            if (end < start) {
                [start, end] = [end, start];
            }

            this.state.startDate = start;
            this.state.endDate = end;
            this.state.focusedDateIndex = 0;
        }
    }

    onApply() {
        if (!this.hasSelection) return;

        const startStr = this.state.startDate.toFormat("yyyy-MM-dd");
        const endStr = this.state.endDate.toFormat("yyyy-MM-dd");

        // Create filter using SearchModel API
        this.props.searchModel.createNewFilters([{
            description: `${this.fieldLabel}: ${this.formattedStart} - ${this.formattedEnd}`,
            domain: [
                [this.fieldName, ">=", startStr],
                [this.fieldName, "<=", endStr],
            ],
            type: "filter",
        }]);

        this.state.isOpen = false;
    }

    onClear() {
        this.state.startDate = false;
        this.state.endDate = false;
        this.state.focusedDateIndex = 0;
    }
}

// Patch SearchPanel to add showDateRangeFilter property
patch(SearchPanel.prototype, {
    setup() {
        super.setup(...arguments);
        const resModel = this.env.searchModel?.resModel;
        this.showDateRangeFilter = MODELS_WITH_DATE_FILTER.includes(resModel);
    }
});

// Add DateRangeFilter to SearchPanel components
SearchPanel.components = { ...SearchPanel.components, DateRangeFilter };
