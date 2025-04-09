import { Component } from '@angular/core';
import { HighlightLoader } from 'ngx-highlightjs';

@Component({
  selector: 'app-code-viewer',
  templateUrl: './code-viewer.component.html',
})
export class CodeViewerComponent {
  highlightedCode = '';

  constructor(private hsloader: HighlightLoader) {}

  async highlightCode(code: string, lang: string): Promise<void> {
    try {
      const result = await this.hsloader.highlight(code, {
        language: lang,
        ignoreIllegals: true,
      });
      this.highlightedCode = result.value;
    } catch (error) {
      console.error('Highlighting failed', error);
    }
  }

  someAction() {
    const code = 'console.log("Hello World");';
    const lang = 'javascript';
    this.highlightCode(code, lang);
  }
}
