from imgui.integrations.pygame import PygameRenderer
import OpenGL.GL as gl
import imgui
import pygame
import sys
from data import GuiDataHolder, Instuction, Program


pygame.init()
W, H = 800, 800
DEBUG = False

pygame.display.set_mode((W, H), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)

imgui.create_context()
impl = PygameRenderer()
io = imgui.get_io()
io.display_size = (W, H)

gui_data = GuiDataHolder()

def compile():
    pass

def center_window():
    imgui.set_next_window_position(io.display_size.x * 0.5, io.display_size.y * 0.5, 1, pivot_x = 0.5, pivot_y = 0.5)

def imgui_editor():
    with imgui.begin_child("right_side", 0, 0, True):
            with imgui.begin_tab_bar("Programs") as tab_bar:
                if tab_bar.opened:
                    for program in gui_data.programs:
                        extra = 0
                        if program.force:
                            extra = imgui.TAB_ITEM_SET_SELECTED
                            program.force = False
                        with imgui.begin_tab_item(program.name, opened=True, flags=imgui.TAB_ITEM_NO_CLOSE_WITH_MIDDLE_MOUSE_BUTTON | extra) as programtab:
                            if not programtab.opened:
                                gui_data.programs.remove(program)

                            if programtab.selected:
                                program.selected = True
                                if imgui.is_item_clicked() and imgui.is_mouse_double_clicked(0):
                                    gui_data.temp["program_name_tmp"] = program.name
                                    imgui.open_popup("Rename Program")

                                center_window()
                                with imgui.begin_popup_modal("Rename Program", True, flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_ALWAYS_AUTO_RESIZE) as popup:
                                    if popup.opened:
                                        _, gui_data.temp["program_name_tmp"] = imgui.input_text("Rename: ", gui_data.temp["program_name_tmp"])
                                        if imgui.button("Rename"):
                                            program.name = gui_data.temp["program_name_tmp"]
                                            program.force = True
                                    
                                _, program.data = imgui.input_text_multiline(f"##Editor{program.id}", program.data, width=-1, height=-1)
                            else:
                                program.selected = False
                                    

                    if imgui.tab_item_button("+"):
                        used_ids = sorted([program.id for program in gui_data.programs]) if len(gui_data.programs) != 0 else [0]
                        c_id = used_ids[-1]+1
                        gui_data.add_program(Program(c_id, f"New Program {c_id}", True, "", True))
# 
def imgui_instruction():
    with imgui.begin_child("left_side", 300, 0, True):
            # Export, Save and other buttons
        with imgui.begin_child("export_buttons", 0, 40, False):
            if imgui.button("Assemble"):
                gui_data.temp["program_selector_tmp"] = 0
                imgui.open_popup("Compiler")
            
            center_window()
            with imgui.begin_popup_modal("Compiler", True, flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_ALWAYS_AUTO_RESIZE) as popup:
                if popup.opened:
                    programs = gui_data.programs
                    imgui.text("Select Program ")
                    imgui.same_line()
                    with imgui.begin_combo("##Program Selector", "No Program To Compile" if len(programs) == 0 else programs[gui_data.temp.get("program_selector_tmp", 0)].name) as combo:
                        if combo.opened and len(programs) != 0:
                            for ind, program in enumerate(programs):
                                if imgui.selectable(program.name, gui_data.temp.get("program_selector_tmp", 0) == ind)[0]:
                                    gui_data.temp["program_selector_tmp"] = ind
                    imgui.text("Output File Path")
                    imgui.same_line()
                    _, gui_data.temp["output_file"] = imgui.input_text("##Output File", gui_data.temp.get("output_file", ""))
                    if imgui.button("Compile"):
                        compile(programs[selected], gui_data.instructions)
                            


        imgui.separator()
            # Instruction Child For List 
        with imgui.begin_child("instructions", 0, 0, False):
                # List instructions
            with imgui.begin_list_box("##instructions_list", 300, -25) as list_box:
                if list_box.opened:
                    for index, instruction in enumerate(gui_data.instructions):
                        _, selected = imgui.selectable(instruction.name, index == gui_data.selected_instruction)
                        if selected:
                            gui_data.selected_instruction = index
                        if selected and imgui.is_mouse_double_clicked(0):
                            gui_data.temp["instruction_name_tmp"] = instruction.name
                            for i in range(8):
                                gui_data.temp[f"instruction_binary_tmp_{i}"] = False if bin(instruction.value)[2:].zfill(8)[i] == "0" else True
                            imgui.open_popup(f"Edit Instruction##{index}")
                        
                        center_window()
                        with imgui.begin_popup_modal(f"Edit Instruction##{index}", True, flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_ALWAYS_AUTO_RESIZE) as popup:
                            if popup.opened:
                                imgui.text("Name:  ")
                                imgui.same_line()
                                changed, gui_data.temp["instruction_name_tmp"] = imgui.input_text("##name", gui_data.temp.get("instruction_name_tmp", ""))
                                if changed:
                                    gui_data.temp["instruction_add_error"] = False
                                    
                                imgui.text("Binary:")
                                for i in range(8):
                                    imgui.same_line()
                                    _, gui_data.temp[f"instruction_binary_tmp_{i}"] = imgui.checkbox(f"##{i}", gui_data.temp.get(f"instruction_binary_tmp_{i}", False))

                                if imgui.button("Edit##popup"):
                                    if name := gui_data.temp.get("instruction_name_tmp", ""):
                                        new_instruction = Instuction(name, int("".join(["1" if gui_data.temp.get(f"instruction_binary_tmp_{i}", False) else "0" for i in range(8)]), base=2))
                                        gui_data.replace_instruction(index, new_instruction)
                                        imgui.close_current_popup()
                                    else:
                                        gui_data.temp["instruction_add_error"] = True
                                    
                                if gui_data.temp.get("instruction_add_error", False):
                                    imgui.push_style_color(imgui.COLOR_TEXT, 1, 0, 0)
                                    imgui.text("Please write a valid instruction name")
                                    imgui.pop_style_color(1)
                
                # Add a new Instruction
            if imgui.button("Add##list"):
                imgui.open_popup("Add Instruction")
                
            center_window()
            with imgui.begin_popup_modal("Add Instruction", True, flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_ALWAYS_AUTO_RESIZE) as popup:
                if popup.opened:
                    imgui.text("Name:  ")
                    imgui.same_line()
                    changed, gui_data.temp["instruction_name_tmp"] = imgui.input_text("##name", gui_data.temp.get("instruction_name_tmp", ""))
                    if changed:
                        gui_data.temp["instruction_add_error"] = False
                        
                    imgui.text("Binary:")
                    for i in range(8):
                        imgui.same_line()
                        _, gui_data.temp[f"instruction_binary_tmp_{i}"] = imgui.checkbox(f"##{i}", gui_data.temp.get(f"instruction_binary_tmp_{i}", False))

                    if imgui.button("Add##popup"):
                        if name := gui_data.temp.get("instruction_name_tmp", ""):
                            new_instruction = Instuction(name, int("".join(["1" if gui_data.temp.get(f"instruction_binary_tmp_{i}", False) else "0" for i in range(8)]), base=2))
                            gui_data.add_instruction(new_instruction)
                            imgui.close_current_popup()
                        else:
                            gui_data.temp["instruction_add_error"] = True
                        
                    if gui_data.temp.get("instruction_add_error", False):
                        imgui.push_style_color(imgui.COLOR_TEXT, 1, 0, 0)
                        imgui.text("Please write a valid instruction name")
                        imgui.pop_style_color(1)

def imgui_render_product():
    with imgui.begin("Assembler"):
        # Instruction and export side
        imgui_instruction()
        imgui.same_line()
        imgui_editor()

def imgui_render_test():
    pass

def imgui_render():
    global DEBUG
    with imgui.begin("Debugger"):
        imgui.text(f"Debug Mode: {DEBUG}")
        if imgui.button("Toggle Debug Mode"):
            DEBUG = not DEBUG

    if DEBUG:
        imgui_render_test()
    else:
        imgui_render_product()


def main():
    while True:
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            impl.process_event(event)
        impl.process_inputs()

        imgui.new_frame()
        imgui_render()
        imgui.render()
        impl.render(imgui.get_draw_data())
        pygame.display.flip()


if __name__ == "__main__":
    main()