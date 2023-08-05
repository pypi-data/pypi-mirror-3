from kaa import imlib2, display, main
from kaa import evas

window = display.X11Window(size = (1024, 768), title = "Kaa Display Test")
#image = imlib2.open("data/background.jpg")
#imlib2.add_font_path("data")
#image.draw_text((50, 50), "This is a Kaa Display Imlib2 Test", (255,255,255,255), "VeraBd/24")
#image = imlib2.new((1024, 768))
import array
b = array.array('c', '\x00' * (1024*768*4))
canvas = evas.EvasBuffer((1024, 768), depth = evas.ENGINE_BUFFER_DEPTH_BGRA32, buffer = b)
canvas.viewport_set((0, 0), (800, 600))
img = canvas.object_image_add("data/background.jpg")
img.show()

canvas.output_size_set((720, 480))
canvas.render()
print canvas.output_size_get()
image = imlib2.new((1024, 768), canvas.buffer_get())
#image = imlib2.new(canvas.output_size_get(), canvas.buffer_get())
window.show()
window.render_imlib2_image(image)
main()
