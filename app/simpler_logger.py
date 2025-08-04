class SimpleLogger {
  write(level, message) {
    const time = new Date().toISOString();
    const log = `[${time}] [${level.toUpperCase()}] ${message}`;
    console.log(log);
    require('fs').appendFileSync('app.log', log + '\n');
  }

  info(msg) { this.write('info', msg); }
  error(msg) { this.write('error', msg); }
}

module.exports = new SimpleLogger();