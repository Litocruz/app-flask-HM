function checkHealth() {
  return {
    status: "OK",
    timestamp: new Date(),
    message: "¡Mi aplicación está funcionando! 🎉"
  };
}

module.exports = { checkHealth };