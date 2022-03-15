import json
import os

def gen_ill_dicts(sim_folder):
    """Given a simulation folder, figure out the possible configurations of ill files to
    be written out after the simulations."""

    with open(os.path.join(sim_folder,'model', 'grid', '_info.json')) as grid_data:
        grid_list= json.load(grid_data)

    with open(os.path.join(sim_folder,'model', 'aperture_group', 'states.json')) as state_data:
        states_dict= json.load(state_data)


    three_phase_dict={}
    two_phase_dict={}
    for grid in grid_list:
        name=grid['name']
        count = grid['name']
        light_paths=grid['light_path']
        for path_lst in light_paths:
            for path in path_lst:
                try:

                    for states in states_dict[path]:
                        if 'tmtx' in states:
                            try:
                                three_phase_dict[name].append(states['identifier'])
                            except KeyError:
                                three_phase_dict[name]=[states['identifier']]

                        else:
                            try:
                                two_phase_dict[name].append(states['identifier'])
                            except KeyError:
                                two_phase_dict[name]=[states['identifier']]


                except KeyError:
                    assert path=='static_apertures','The key error occurred due to %s'%path
                    try:
                        two_phase_dict[name].append(path)
                    except KeyError:
                        two_phase_dict[name] = [path]

    return two_phase_dict,three_phase_dict

def gen_ill_paths(sim_folder,ill_dicts):
    """Given a dictionary containing possible ill combinations generate lists of paths
    for two phase and three phase runs."""

    two_phase_dict,three_phase_dict=ill_dicts

    two_phase_list = []
    for room,aperture_list in two_phase_dict.items():
        for aperture in aperture_list:
            if aperture=='static_apertures':
                two_phase_list.append(os.path.join(sim_folder,'results','2_phase','__static_apertures__','%s.ill'%room))
            else:
                two_phase_list.append(os.path.join(sim_folder,'results','2_phase',aperture,'%s.ill'%room))

    three_phase_list=[]
    for room,aperture_list in three_phase_dict.items():
        for aperture in aperture_list:
            three_phase_list.append((os.path.join(sim_folder,'results','3_phase','%s..%s.ill'%(room,aperture))))

    return two_phase_list,three_phase_list

def get_created_ill_paths(sim_folder):
    """Create lists of all the three phase and two phase files that were actually
    generated during the simulation"""
    three_phase_res_dir=os.path.join(sim_folder,'results','3_phase')
    three_phase_ills=[os.path.join(three_phase_res_dir,path) for path in os.listdir(three_phase_res_dir) if path.endswith('.ill')]

    two_phase_res_root=os.path.join(sim_folder,'results','2_phase')
    two_phase_ills=[]
    for sub_dir in os.listdir(two_phase_res_root):
        sub_dir=os.path.join(two_phase_res_root,sub_dir)
        if os.path.isdir(sub_dir):
            two_phase_ills.extend([os.path.join(sub_dir,path) for path in os.listdir(sub_dir) if path.endswith('.ill')])

    return two_phase_ills,three_phase_ills

def audit_ill_files(sim_folder):
    """Compare the required and existing files for two and three phase runs and generate
    a dictionary comprising of missing and redudnant file lists."""
    req_2ph,req_3ph=gen_ill_paths(sim_folder,gen_ill_dicts(sim_folder))
    exist_2ph,exist_3ph=get_created_ill_paths(sim_folder)

    redun_2ph=[path for path in exist_2ph if path not in req_2ph]
    miss_2ph=[path for path in req_2ph if path not in exist_2ph]

    redun_3ph = [path for path in exist_3ph if path not in req_3ph]
    miss_3ph = [path for path in req_3ph if path not in exist_3ph]

    return {'redundant_2ph':redun_2ph,
            'redundant_3ph':redun_3ph,'missing_2ph':miss_2ph,'missing_3ph':miss_3ph}




if __name__ == '__main__':
    folder = r'/mnt/sdb/three-phase/new_run_greg_param/project_folder/three_phase_164634387089'
    for file_type,file_list in audit_ill_files(folder).items():
        if file_list:
            print('The following files are the %s files'%file_type)
            for file_path in file_list:
                print('\t'+file_path)