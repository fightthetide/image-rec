import os

class DataLayer:
  def save_result(self, result, path):
    # Example: Save results to disk
    with open(path, 'w') as f:
      f.write(str(result))

  def load_data(self, path):
    # Example: Load data from disk
    if os.path.exists(path):
      with open(path, 'r') as f:
        return f.read()
    return None
