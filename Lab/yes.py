import ctypes
import random
import time
import os
import struct

MAX_NAME_LENGTH = 50
NUM_STUDENTS = 100
DATA_FILE = "students.dat"

CATEGORY_NAMES = [b"homework", b"quizzes", b"midterm", b"final"]
CATEGORY_WEIGHTS = [0.2, 0.2, 0.25, 0.35]


class CStudent(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("name", ctypes.c_char * MAX_NAME_LENGTH),
        ("scores", ctypes.c_float * 4),
        ("final_grade", ctypes.c_float),
        ("letter_grade", ctypes.c_char * 3)
    ]


class MemoryManager:
    def __init__(self, capacity):
        self.capacity = capacity
        self.storage = (ctypes.POINTER(CStudent) * capacity)()
        self.allocated = [False] * capacity

    def malloc(self):
        for i in range(self.capacity):
            if not self.allocated[i]:
                ptr = ctypes.pointer(CStudent())
                self.storage[i] = ptr
                self.allocated[i] = True
                return i, ptr
        raise MemoryError("No more memory available!")

    def free(self, index):
        if self.allocated[index]:
            self.allocated[index] = False
            self.storage[index] = None
            print(f"[INFO] Freed memory slot {index}")
        else:
            print(f"[WARN] Slot {index} already free")

    def get_allocated_students(self):
        return [(i, self.storage[i]) for i, used in enumerate(self.allocated) if used]


def assign_letter_grade(score):
    if score >= 97:
        return b"A+"
    elif score >= 93:
        return b"A"
    elif score >= 90:
        return b"A-"
    elif score >= 87:
        return b"B+"
    elif score >= 83:
        return b"B"
    elif score >= 80:
        return b"B-"
    elif score >= 77:
        return b"C+"
    elif score >= 73:
        return b"C"
    elif score >= 70:
        return b"C-"
    elif score >= 67:
        return b"D+"
    elif score >= 63:
        return b"D"
    elif score >= 60:
        return b"D-"
    else:
        return b"F "


def calculate_final_grade(student_ptr):
    total = 0.0
    for i in range(4):
        total += student_ptr.contents.scores[i] * CATEGORY_WEIGHTS[i]
    student_ptr.contents.final_grade = round(total, 2)
    student_ptr.contents.letter_grade = (ctypes.c_char * 3)(*assign_letter_grade(total))


def create_random_student(index):
    name = f"Student_{index}".encode("utf-8").ljust(MAX_NAME_LENGTH, b'\x00')
    scores = (ctypes.c_float * 4)(*[round(random.uniform(60, 100), 2) for _ in range(4)])
    student = CStudent(
        id=index,
        name=(ctypes.c_char * MAX_NAME_LENGTH)(*name),
        scores=scores,
        final_grade=0.0,
        letter_grade=(ctypes.c_char * 3)(*b"--")
    )
    return student


def print_student(student_ptr):
    student = student_ptr.contents
    name = student.name.decode().strip('\x00')
    print(f"\n=== Report Card for {name} ===")
    for i in range(4):
        print(f"{CATEGORY_NAMES[i].decode().capitalize()}: {student.scores[i]}")
    print(f"Final Grade: {student.final_grade}")
    print(f"Letter Grade: {student.letter_grade.decode().strip()}")
    print("=" * 30)


def save_to_binary_file(memory_manager):
    with open(DATA_FILE, "wb") as f:
        for i, ptr in memory_manager.get_allocated_students():
            f.write(bytes(ptr.contents))
    print(f"[INFO] Saved to {DATA_FILE}")


def load_from_binary_file(memory_manager):
    if not os.path.exists(DATA_FILE):
        print("[ERROR] No file to load.")
        return
    with open(DATA_FILE, "rb") as f:
        while True:
            chunk = f.read(ctypes.sizeof(CStudent))
            if not chunk:
                break
            index, ptr = memory_manager.malloc()
            ctypes.memmove(ctypes.addressof(ptr.contents), chunk, ctypes.sizeof(CStudent))
    print("[INFO] Loaded students from file.")


def run_shell():
    mm = MemoryManager(NUM_STUDENTS)
    print("Welcome to the GradeMachine 9000™ (C Edition)\nType 'help' for commands.")

    while True:
        cmd = input("grade-machine> ").strip().lower()

        if cmd == "help":
            print("\nCommands:")
            print("  malloc     - Allocate a new student (random data)")
            print("  free N     - Free student at slot N")
            print("  show       - Show all allocated students")
            print("  save       - Save all students to binary file")
            print("  load       - Load students from binary file")
            print("  exit       - Exit the program\n")

        elif cmd == "malloc":
            try:
                index, ptr = mm.malloc()
                student = create_random_student(index)
                ctypes.memmove(ctypes.addressof(ptr.contents), ctypes.addressof(student), ctypes.sizeof(CStudent))
                calculate_final_grade(ptr)
                print_student(ptr)
            except MemoryError as e:
                print(f"[ERROR] {e}")

        elif cmd.startswith("free"):
            parts = cmd.split()
            if len(parts) != 2 or not parts[1].isdigit():
                print("[ERROR] Usage: free N")
                continue
            mm.free(int(parts[1]))

        elif cmd == "show":
            for i, ptr in mm.get_allocated_students():
                print(f"\n[Memory Slot {i}]")
                print_student(ptr)

        elif cmd == "save":
            save_to_binary_file(mm)

        elif cmd == "load":
            load_from_binary_file(mm)

        elif cmd == "exit":
            print("Exiting GradeMachine 9000. Goodbye.")
            break

        else:
            print("[ERROR] Unknown command. Type 'help'.")


if __name__ == "__main__":
    run_shell()
