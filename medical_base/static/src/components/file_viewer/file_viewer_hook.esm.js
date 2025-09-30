/** @odoo-module **/

import {FileViewer} from "./file_viewer.esm";
import {onWillDestroy} from "@odoo/owl";
import {registry} from "@web/core/registry";

let id = 1;

export function createFileViewer() {
    const fileViewerId = `web.file_viewer${id++}`;
    function open(file, files = [file]) {
        if (!file.isViewable) {
            return;
        }
        if (files.length > 0) {
            const viewableFiles = files.filter((filter_file) => filter_file.isViewable);
            const index = viewableFiles.indexOf(file);
            registry.category("main_components").add(fileViewerId, {
                Component: FileViewer,
                props: {files: viewableFiles, startIndex: index, close: this.close},
            });
        }
    }

    function close() {
        registry.category("main_components").remove(fileViewerId);
    }
    return {open, close};
}

export function useFileViewer() {
    const {open, close} = createFileViewer();
    onWillDestroy(close);
    return {open, close};
}
