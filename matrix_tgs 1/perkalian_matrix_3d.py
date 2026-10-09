A = [
    [[1, 2], [3, 4]],
    [[3, 4], [4, 5]]
]

B = [
    [[9, 8], [5, 4]],
    [[1, 7], [3, 1]]
]

print("=== ARRAY A ===")

for k in range(2):
    print("Matriks", k + 1)
    for baris in A[k]:
        print(baris)
    print()

print("=== ARRAY B ===")

for k in range(2):
    print("Matriks", k + 1)
    for baris in B[k]:
        print(baris)
    print()
    
hasil = []

for k in range(2):
    matriks = []

    for i in range(2):
        baris = []

        for j in range(2):
            jumlah = 0

            for x in range(2):
                jumlah += A[k][i][x] * B[k][x][j]

            baris.append(jumlah)

        matriks.append(baris)

    hasil.append(matriks)

print("=== HASIL A x B ===")

for k in range(2):
    print("Matriks", k + 1)
    for baris in hasil[k]:
        print(baris)
    print()