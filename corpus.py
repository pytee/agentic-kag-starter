"""Tiny campus dataset with a hidden multi-hop chain:
Machine Learning (taught by Lina) -> prerequisite for -> Robotics
(taught by Omar) -> uses -> PixelKit -> built by -> Vision Lab -> led by -> Lina.

Good test question: "Who teaches the prerequisite for the course that uses PixelKit?"
"""

DOCUMENTS = [
    {
        "id": "doc1",
        "text": (
            "Dr. Lina Cheong teaches Machine Learning at Summit University. "
            "She leads the Vision Lab and supervises final-year projects. "
            "Lina completed her PhD at Coastal Tech in 2015."
        ),
    },
    {
        "id": "doc2",
        "text": (
            "The Vision Lab built an open-source library called PixelKit. "
            "PixelKit is used in the Robotics course taught by Dr. Omar Faiz. "
            "Omar also studied at Coastal Tech."
        ),
    },
    {
        "id": "doc3",
        "text": (
            "Coastal Tech is a research university known for computer vision. "
            "Its most cited alumnus is Dr. Lina Cheong. "
            "The Robotics course at Summit University requires Machine Learning "
            "as a prerequisite."
        ),
    },
]
