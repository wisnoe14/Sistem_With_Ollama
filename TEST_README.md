# Test untuk Conversation Flow Telecollection
# Sesuai spesifikasi alur yang diberikan

# EXPECTED FLOW:
# 1. Opening: "Selamat pagi/siang/sore. Perkenalkan saya dari ICONNET, apakah benar saya terhubung dengan Bapak/Ibu pemilik layanan? Mohon maaf, Apakah bapak/ibu sudah melakukan pembayaran bulanan ICONNET?"
#    Options: ["Ya, sudah bayar", "Belum bayar", "Bukan saya", "Siapa ini?"]

# 2A. Jika "Ya, sudah bayar" -> CLOSING: "Baik terima kasih atas konfirmasinya pak/bu, mohon maaf mengganggu waktunya, selamat pagi/siang/sore"

# 2B. Jika "Belum bayar" -> Payment Reminder: "Baik pak/bu, izin mengingatkan mengenai pembayaran ICONNET bulanannya yaa..."
#     Options: ["Iya", "Baik", "Ada keluhan", "Kapan bayar?"]

# 3A. Jika "Iya/Baik" -> Payment Timing: "Baik bapak/ibu, sekiranya kapan akan melakukan pembayaran ya bapak/ibu?"
#     Options: ["Hari ini", "Besok", "Akhir pekan", "Masih ada kendala"]

# 4A. Jika timing specific -> CLOSING: "Baik bapak/ibu, Terima kasih atas waktu dan konfirmasinya..."

# Test scenarios:
print("=== CONVERSATION FLOW TEST SCENARIOS ===")
print()
print("SCENARIO 1 - SUDAH BAYAR:")
print("User: Ya, sudah bayar")
print("Expected: CLOSING message")
print()
print("SCENARIO 2 - BELUM BAYAR:")
print("User: Belum bayar -> Iya -> Hari ini")
print("Expected: Payment reminder -> Payment timing -> CLOSING")
print()
print("SCENARIO 3 - ADA KELUHAN:")
print("User: Belum bayar -> Ada keluhan -> Tidak ada")
print("Expected: Payment reminder -> Complaint handling -> CLOSING")
print()
print("Backend server is running on http://localhost:8000")
print("You can now test the conversation flow through the frontend!")