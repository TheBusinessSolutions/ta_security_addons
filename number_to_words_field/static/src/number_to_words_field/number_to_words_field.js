/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { formatFloatTime } from "@web/views/fields/formatters";
import { parseFloatTime } from "@web/views/fields/parsers";
import { useInputField } from "@web/views/fields/input_field_hook";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useNumpadDecimal } from "@web/views/fields/numpad_decimal_hook";

import { FloatField } from "@web/views/fields/float/float_field";

import { formatFloat } from "@web/core/utils/numbers";

import { Component, useState  } from "@odoo/owl";

export class FloatToCharField extends Component {
    static template = "interger_on_float_field.FloatToChar";
    static props = {
        ...standardFieldProps,
        formatNumber: { type: Boolean, optional: true },
        inputType: { type: String, optional: true },
        placeholder: { type: String, optional: true },
        step: { type: Number, optional: true },
        digits: { type: Array, optional: true },
        displaySeconds: { type: Boolean, optional: true },
        humanReadable: { type: Boolean, optional: true },
        decimals: { type: Number, optional: true },
    };
    static defaultProps = {
        formatNumber: true,
        inputType: "text",
        humanReadable: false,
        decimals: 0,
    };

    setup() {
        this.state = useState({
            hasFocus: false,
        });
        useInputField({
            getValue: () => this.formattedValue,
            refName: "numpadDecimal",
            parse: (v) => parseFloatTime(v),
        });
        useNumpadDecimal();
    }

    onFocusIn() {
        this.state.hasFocus = true;
    }

    onFocusOut() {
        this.state.hasFocus = false;
    }

    get digits() {
        const fieldDigits = this.props.record.fields[this.props.name].digits;
        return !this.props.digits && Array.isArray(fieldDigits) ? fieldDigits : this.props.digits;
    }

    get value() {
        return this.props.record.data[this.props.name];
    }

    get formattedValue() {
        if(this.props.readonly){
            return numberToWords(this.value);
        }else{
            if (this.props.humanReadable && !this.state.hasFocus) {
                return formatFloat(this.value, {
                    digits: this.digits,
                    humanReadable: true,
                    decimals: this.props.decimals,
                });
            } else {
                return formatFloat(this.value, { digits: this.digits, humanReadable: false });
            }
        }
    }
}

export const floatToCharField = {
    component: FloatToCharField,
    displayName: _t("English Number"),
    supportedOptions: [
        {
            label: _t("Format number"),
            name: "enable_formatting",
            type: "boolean",
            help: _t(
                "Format the value according to your language setup - e.g. thousand separators, rounding, etc."
            ),
            default: true,
        },
        {
            label: _t("Digits"),
            name: "digits",
            type: "string",
        },
        {
            label: _t("Type"),
            name: "type",
            type: "string",
        },
        {
            label: _t("Step"),
            name: "step",
            type: "number",
        },
        {
            label: _t("User-friendly format"),
            name: "human_readable",
            type: "boolean",
            help: _t("Use a human readable format (e.g.: 500G instead of 500,000,000,000)."),
        },
        {
            label: _t("Decimals"),
            name: "decimals",
            type: "number",
            default: 0,
            help: _t("Use it with the 'User-friendly format' option to customize the formatting."),
        },
    ],
    supportedTypes: ["float"],
    isEmpty: () => false,
    extractProps: ({ attrs, options }) => {
        let digits;
        if (attrs.digits) {
            digits = JSON.parse(attrs.digits);
        } else if (options.digits) {
            digits = options.digits;
        }

        return {
            formatNumber:
                options?.enable_formatting !== undefined
                    ? Boolean(options.enable_formatting)
                    : true,
            inputType: options.type,
            humanReadable: !!options.human_readable,
            step: options.step,
            digits,
            placeholder: attrs.placeholder,
            decimals: options.decimals || 0,
        };
    },
};

registry.category("fields").add("number_to_words", floatToCharField);
