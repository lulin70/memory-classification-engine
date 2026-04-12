const vscode = require('vscode');
const axios = require('axios');

class MemoryClassificationEngine {
    constructor() {
        this.baseUrl = 'http://localhost:8000'; // MCP Server URL
        this.memories = [];
        this.context = 'general';
    }

    async recall(context = 'general', limit = 5) {
        try {
            const response = await axios.post(`${this.baseUrl}/tools/call`, {
                jsonrpc: '2.0',
                id: 1,
                method: 'tools/call',
                params: {
                    name: 'mce_recall',
                    arguments: {
                        context: context,
                        limit: limit,
                        format: 'json'
                    }
                }
            });
            
            if (response.data.result && response.data.result.content) {
                const content = JSON.parse(response.data.result.content[0].text);
                this.memories = content.memories || [];
                return this.memories;
            }
            return [];
        } catch (error) {
            console.error('Error recalling memories:', error);
            return [];
        }
    }

    async getStatus(detailLevel = 'summary') {
        try {
            const response = await axios.post(`${this.baseUrl}/tools/call`, {
                jsonrpc: '2.0',
                id: 1,
                method: 'tools/call',
                params: {
                    name: 'mce_status',
                    arguments: {
                        detail_level: detailLevel
                    }
                }
            });
            
            if (response.data.result && response.data.result.content) {
                const content = JSON.parse(response.data.result.content[0].text);
                return content;
            }
            return null;
        } catch (error) {
            console.error('Error getting memory status:', error);
            return null;
        }
    }

    async forget(memoryId, reason = 'user_request') {
        try {
            const response = await axios.post(`${this.baseUrl}/tools/call`, {
                jsonrpc: '2.0',
                id: 1,
                method: 'tools/call',
                params: {
                    name: 'mce_forget',
                    arguments: {
                        memory_id: memoryId,
                        reason: reason
                    }
                }
            });
            
            if (response.data.result && response.data.result.content) {
                const content = JSON.parse(response.data.result.content[0].text);
                return content;
            }
            return null;
        } catch (error) {
            console.error('Error forgetting memory:', error);
            return null;
        }
    }

    async exportMemories() {
        try {
            const response = await axios.post(`${this.baseUrl}/tools/call`, {
                jsonrpc: '2.0',
                id: 1,
                method: 'tools/call',
                params: {
                    name: 'export_memories',
                    arguments: {
                        format: 'json'
                    }
                }
            });
            
            if (response.data.result && response.data.result.content) {
                const content = JSON.parse(response.data.result.content[0].text);
                return content.data;
            }
            return null;
        } catch (error) {
            console.error('Error exporting memories:', error);
            return null;
        }
    }

    async importMemories(data) {
        try {
            const response = await axios.post(`${this.baseUrl}/tools/call`, {
                jsonrpc: '2.0',
                id: 1,
                method: 'tools/call',
                params: {
                    name: 'import_memories',
                    arguments: {
                        data: data,
                        format: 'json'
                    }
                }
            });
            
            if (response.data.result && response.data.result.content) {
                const content = JSON.parse(response.data.result.content[0].text);
                return content;
            }
            return null;
        } catch (error) {
            console.error('Error importing memories:', error);
            return null;
        }
    }
}

class MemoryTreeDataProvider {
    constructor(mce) {
        this.mce = mce;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }

    refresh() {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element) {
        return element;
    }

    async getChildren(element) {
        if (!element) {
            // Root level - show memory categories
            const memories = await this.mce.recall();
            
            // Group memories by type
            const grouped = {};
            memories.forEach(memory => {
                const type = memory.type || 'unknown';
                if (!grouped[type]) {
                    grouped[type] = [];
                }
                grouped[type].push(memory);
            });

            // Create category items
            const categories = Object.keys(grouped).map(type => {
                return new MemoryCategory(type, grouped[type].length);
            });

            return categories;
        } else if (element instanceof MemoryCategory) {
            // Category level - show memories
            const memories = await this.mce.recall();
            const filtered = memories.filter(memory => memory.type === element.label);
            
            return filtered.map(memory => new MemoryItem(memory));
        }
        return [];
    }
}

class MemoryCategory extends vscode.TreeItem {
    constructor(label, count) {
        super(label, vscode.TreeItemCollapsibleState.Collapsed);
        this.count = count;
        this.tooltip = `${label}: ${count} memories`;
        this.description = `${count}`;
    }
}

class MemoryItem extends vscode.TreeItem {
    constructor(memory) {
        super(memory.content, vscode.TreeItemCollapsibleState.None);
        this.memory = memory;
        this.tooltip = `Type: ${memory.type}\nConfidence: ${memory.confidence || 0}\nCreated: ${memory.created_at || 'Unknown'}`;
        this.description = `${memory.confidence || 0}`;
        this.contextValue = 'memory';
        this.id = memory.id;
    }
}

function activate(context) {
    console.log('Memory Classification Engine extension activated');

    const mce = new MemoryClassificationEngine();
    const treeDataProvider = new MemoryTreeDataProvider(mce);

    vscode.window.registerTreeDataProvider('memoryClassificationEngine', treeDataProvider);

    // Commands
    context.subscriptions.push(
        vscode.commands.registerCommand('memoryClassificationEngine.recall', async () => {
            const memories = await mce.recall();
            treeDataProvider.refresh();
            vscode.window.showInformationMessage(`Recalled ${memories.length} memories`);
        }),

        vscode.commands.registerCommand('memoryClassificationEngine.status', async () => {
            const status = await mce.getStatus();
            if (status) {
                const stats = status.stats;
                const message = `Memory Status:\nTotal: ${stats.total_memories}\nTypes: ${Object.keys(stats.by_type || {}).length}\nHigh Quality: ${stats.high_quality_memories || 0}`;
                vscode.window.showInformationMessage(message);
            } else {
                vscode.window.showErrorMessage('Failed to get memory status');
            }
        }),

        vscode.commands.registerCommand('memoryClassificationEngine.forget', async (item) => {
            if (item && item.id) {
                const result = await mce.forget(item.id);
                if (result && result.success) {
                    treeDataProvider.refresh();
                    vscode.window.showInformationMessage('Memory forgotten successfully');
                } else {
                    vscode.window.showErrorMessage('Failed to forget memory');
                }
            }
        }),

        vscode.commands.registerCommand('memoryClassificationEngine.export', async () => {
            const data = await mce.exportMemories();
            if (data) {
                const path = await vscode.window.showSaveDialog({
                    filters: { 'JSON': ['json'] },
                    defaultFile: 'memories.json'
                });
                if (path) {
                    const fs = require('fs');
                    fs.writeFileSync(path.fsPath, data);
                    vscode.window.showInformationMessage('Memories exported successfully');
                }
            } else {
                vscode.window.showErrorMessage('Failed to export memories');
            }
        }),

        vscode.commands.registerCommand('memoryClassificationEngine.import', async () => {
            const path = await vscode.window.showOpenDialog({
                filters: { 'JSON': ['json'] }
            });
            if (path && path[0]) {
                const fs = require('fs');
                const data = fs.readFileSync(path[0].fsPath, 'utf8');
                const result = await mce.importMemories(data);
                if (result && result.success) {
                    treeDataProvider.refresh();
                    vscode.window.showInformationMessage(`Imported ${result.imported_count} memories`);
                } else {
                    vscode.window.showErrorMessage('Failed to import memories');
                }
            }
        })
    );
}

function deactivate() {
    console.log('Memory Classification Engine extension deactivated');
}

module.exports = {
    activate,
    deactivate
};