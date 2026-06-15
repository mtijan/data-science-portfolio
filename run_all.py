import subprocess
import sys
import time

def main():
    print("Memulai semua layanan...")
    
    # Daftar perintah untuk dijalankan
    commands = [
        ["uv", "run", "python", "manage.py", "runserver"],
        ["uv", "run", "python", "projects/sales_dashboard/dashboard/app.py"],
        ["uv", "run", "python", "projects/churn_prediction/dashboard/app.py"],
        ["uv", "run", "python", "projects/ai_document_assistant/dashboard/app.py"]
    ]
    
    processes = []
    
    try:
        # Menjalankan setiap perintah sebagai subprocess
        for cmd in commands:
            print(f"Menjalankan: {' '.join(cmd)}")
            # stdout dan stderr tidak ditangkap agar langsung tampil di terminal
            process = subprocess.Popen(cmd)
            processes.append(process)
            
        print("\nSemua layanan berhasil dijalankan di background (terminal ini).")
        print("Akses lokal:")
        print("- Portfolio: http://127.0.0.1:8000/")
        print("- Sales Dashboard: http://127.0.0.1:8050/")
        print("- Churn Dashboard: http://127.0.0.1:8051/")
        print("- AI Assistant: http://127.0.0.1:8052/")
        print("\nTekan Ctrl+C untuk menghentikan semua layanan.\n")
        
        # Biarkan script berjalan sampai diinterupsi
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nMenghentikan semua layanan...")
        for p in processes:
            p.terminate()
        
        # Tunggu semua proses selesai
        for p in processes:
            p.wait()
            
        print("Semua layanan telah dihentikan.")
        sys.exit(0)

if __name__ == "__main__":
    main()
