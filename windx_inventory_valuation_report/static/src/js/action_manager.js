/** @odoo-module **/

import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";
import { BlockUI, unBlockUI } from "@web/core/ui/block_ui";

registry.category("ir.actions.report handlers").add("windx_inventory_valuation_xlsx", async (action, options, env) => {
    BlockUI;
    if (action.type === "ir.actions.report" && action.report_type === "windx_inventory_valuation_xlsx") {
        try {

            const wizardId = action.wizard_id || action.context?.active_id;
            const url = `/inventory_valuation/xlsx?wizard_id=${wizardId}`;

            await download({ url,data:{} });
        } catch (error) {
            console.error("Failed to download Excel report:", error);
        } finally {
            unBlockUI;
            env.services.action.doAction({ type: "ir.actions.act_window_close" });
        }
        // Prevent Odoo default error log:
        return true;
    }
});