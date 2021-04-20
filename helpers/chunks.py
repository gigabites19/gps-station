from collections.abc import Iterable, Generator


def get_chunks(iterable: Iterable, chunk_size: int) -> Generator:
    """
    Divides any iterable object into equal parts.

    :param iterable: Any iterable, list, dict, range(), string etc...
    :type iterable: Iterable
    :param chunk_size: Size of the chunks
    :type chunk_size: int
    :returns: Generator that divides iterable in equal parts
    :rtype: Generator
    """
    for i in range(0, len(iterable), chunk_size):
        yield iterable[i:i+chunk_size]
