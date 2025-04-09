this.hsloader.highlight(code, { language: lang, ignoreIllegals: true })
  .then((result: any) => {
    highlightedCode = result.value;
  })
  .catch((error: any) => {
    console.error('Highlighting failed', error);
  });
