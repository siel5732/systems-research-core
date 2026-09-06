/*
ad5m_camera_magnetic_mount.scad
Sleek, Parametric Dual-Lens Magnetic Mount for the ELP Binocular Camera.
Designed to clip to the inside glass panel of the Flashforge AD5M DIY PETG enclosure.

Features:
- Dual lens apertures matching standard ELP binocular spacing.
- 4x Corner recesses for Neodymium N52 disc magnets (8mm x 2mm).
- Snap-fit clips to hold the 80mm x 16mm camera PCB.
- Perfectly flat face for flush mounting to the glass pane.
*/

// --- USER PARAMETERS (Adjustable) ---
pcb_width = 80.5;       // Tolerance added
pcb_height = 16.5;      // Tolerance added
pcb_thickness = 1.6;    
lens_spacing = 40.0;    // Center-to-center distance between dual lenses
lens_diameter = 12.5;   // Diameter of the lens housing
bezel_thickness = 2.0;  // Front face thickness
wall_thickness = 1.5;   // Side wall thickness

magnet_dia = 8.2;       // Tolerance added for 8mm disc magnets
magnet_depth = 2.2;     // Tolerance added for 2mm deep magnets

$fn = 100;              // High resolution curves

module camera_mount_inside() {
    difference() {
        // Main outer bracket shell
        translate([-(pcb_width/2 + wall_thickness), -(pcb_height/2 + wall_thickness), 0])
            cube([pcb_width + 2*wall_thickness, pcb_height + 2*wall_thickness, bezel_thickness + pcb_thickness + 2.0]);
        
        // Inner cutout nested for the PCB
        translate([-pcb_width/2, -pcb_height/2, bezel_thickness])
            cube([pcb_width, pcb_height, pcb_thickness + 5.0]);
        
        // Left Lens Aperture
        translate([-lens_spacing/2, 0, -1])
            cylinder(h = bezel_thickness + 3, d = lens_diameter);
            
        // Right Lens Aperture
        translate([lens_spacing/2, 0, -1])
            cylinder(h = bezel_thickness + 3, d = lens_diameter);
            
        // 4x Corner Magnet Recesses (to be placed flush to the glass side, so on the front face)
        // Top Left Magnet
        translate([-(pcb_width/2 - 5), (pcb_height/2 - 5), -0.1])
            cylinder(h = magnet_depth + 0.1, d = magnet_dia);
            
        // Top Right Magnet
        translate([(pcb_width/2 - 5), (pcb_height/2 - 5), -0.1])
            cylinder(h = magnet_depth + 0.1, d = magnet_dia);
            
        // Bottom Left Magnet
        translate([-(pcb_width/2 - 5), -(pcb_height/2 - 5), -0.1])
            cylinder(h = magnet_depth + 0.1, d = magnet_dia);
            
        // Bottom Right Magnet
        translate([(pcb_width/2 - 5), -(pcb_height/2 - 5), -0.1])
            cylinder(h = magnet_depth + 0.1, d = magnet_dia);
    }
    
    // Add snap-fit clips on the top and bottom edges
    translate([-pcb_width/4, -(pcb_height/2 + wall_thickness), bezel_thickness + pcb_thickness])
        clip_lip();
    translate([pcb_width/4, -(pcb_height/2 + wall_thickness), bezel_thickness + pcb_thickness])
        clip_lip();
    
    translate([-pcb_width/4, pcb_height/2, bezel_thickness + pcb_thickness])
        rotate([0, 0, 180])
            clip_lip();
    translate([pcb_width/4, pcb_height/2, bezel_thickness + pcb_thickness])
        rotate([0, 0, 180])
            clip_lip();
}

module clip_lip() {
    // A tiny geometric overhang that holds the PCB down
    difference() {
        cube([10, wall_thickness, 1.5]);
        translate([-0.1, -0.1, 1.5])
            rotate([30, 0, 0])
                cube([10.2, wall_thickness + 0.2, 2]);
    }
}

module outside_anchor_plaque() {
    // Decorative external plate that aligns with the magnets on the outside of the glass
    difference() {
        union() {
            // Main solid body
            translate([-(pcb_width/2 + wall_thickness), -(pcb_height/2 + wall_thickness), 0])
                cube([pcb_width + 2*wall_thickness, pcb_height + 2*wall_thickness, bezel_thickness]);
                
            // Decorative Metatron-inspired center engraving or plate styling can go here
        }
        
        // 4x Corner Magnet Recesses to align perfectly with the inside mount
        // Top Left Magnet
        translate([-(pcb_width/2 - 5), (pcb_height/2 - 5), bezel_thickness - magnet_depth])
            cylinder(h = magnet_depth + 0.1, d = magnet_dia);
            
        // Top Right Magnet
        translate([(pcb_width/2 - 5), (pcb_height/2 - 5), bezel_thickness - magnet_depth])
            cylinder(h = magnet_depth + 0.1, d = magnet_dia);
            
        // Bottom Left Magnet
        translate([-(pcb_width/2 - 5), -(pcb_height/2 - 5), bezel_thickness - magnet_depth])
            cylinder(h = magnet_depth + 0.1, d = magnet_dia);
            
        // Bottom Right Magnet
        translate([(pcb_width/2 - 5), -(pcb_height/2 - 5), bezel_thickness - magnet_depth])
            cylinder(h = magnet_depth + 0.1, d = magnet_dia);
    }
}

// Render both side-by-side for preview
camera_mount_inside();

translate([0, pcb_height + 15, 0])
    outside_anchor_plaque();
