class LogStore {
  constructor(limit = 300) {
    this.limit = limit;
    this.entries = [];
  }

  add(level, message, detail = '') {
    const entry = {
      level,
      message,
      detail,
      time: new Date().toISOString()
    };
    this.entries.push(entry);
    if (this.entries.length > this.limit) {
      this.entries.shift();
    }
    return entry;
  }

  all() {
    return [...this.entries];
  }
}

module.exports = {
  LogStore
};
