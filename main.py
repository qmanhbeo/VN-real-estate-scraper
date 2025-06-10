from scripts import appendData, cleanData, imputeData, preprocessData, descStats

def run_pipeline():
    print("\n🧩 Step 1: Appending CSVs...")
    appendData.run()

    print("\n🧼 Step 2: Imputing variables...")
    imputeData.run()

    print("\n🔍 Step 3: Cleaning data...")
    cleanData.run()

    print("\n🧠 Step 4: Preprocessing data...")
    preprocessData.run()

    print("\n📊 Step 5: Descriptive stats...")
    descStats.run()

if __name__ == "__main__":
    run_pipeline()
