import random


def generate_closest_array(target, length, min_val=1, max_val=100):
    """
    Genera un array di numeri interi di lunghezza specificata, la cui media è vicina al target.

    :param target: float - Numero float target per la media
    :param length: int - Lunghezza dell'array da generare
    :param min_val: int - Valore minimo degli elementi nell'array
    :param max_val: int - Valore massimo degli elementi nell'array
    :return: List[int] - Array di numeri interi la cui media è vicina al target
    """
    if length <= 0 or min_val > max_val:
        raise ValueError("Input non valido")

    # Genera un array casuale iniziale
    array = [random.randint(min_val, max_val) for _ in range(length)]

    # Calcola la media iniziale
    current_mean = sum(array) / length

    # Tenta di avvicinare la media al target regolando gli elementi dell'array
    for _ in range(10000):  # Limita il numero di iterazioni per evitare loop infiniti
        diff = target - current_mean
        if abs(diff) < 1e-1:  # Se la differenza è abbastanza piccola, fermati
            break

        # Scegli un elemento casuale dell'array
        idx = random.randint(0, length - 1)

        # Modifica l'elemento per avvicinare la media al target
        if diff > 0:
            array[idx] = min(array[idx] + 1, max_val)
        else:
            array[idx] = max(array[idx] - 1, min_val)

        # Ricalcola la media
        current_mean = sum(array) / length

    return array
