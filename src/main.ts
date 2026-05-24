import Phaser from 'phaser';

const W = 480;
const H = 320;
const SPEED = 120;
const DIRS = ['S', 'SE', 'E', 'NE', 'N', 'NW', 'W', 'SW'] as const;
type Direction = (typeof DIRS)[number];

const ANGLE_DIRS: Direction[] = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE'];

function dirFromVelocity(vx: number, vy: number): Direction {
  const angle = Math.atan2(-vy, vx);
  const idx = Math.round(((angle + Math.PI * 2) % (Math.PI * 2)) / (Math.PI / 4)) % 8;
  return ANGLE_DIRS[idx];
}

class RobotScene extends Phaser.Scene {
  private robot!: Phaser.Physics.Arcade.Sprite;
  private egg!: Phaser.Physics.Arcade.Sprite;
  private eggArmed = true;
  private facing: Direction = 'S';
  private keys!: Record<'up' | 'down' | 'left' | 'right', Phaser.Input.Keyboard.Key>;
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private confirmKeys!: Phaser.Input.Keyboard.Key[];
  private popup!: Phaser.GameObjects.Image;
  private popupBulb!: Phaser.GameObjects.Sprite;
  private hoverBulb!: Phaser.GameObjects.Sprite;
  private popupOpen = false;
  private bulbOn = false;
  private popupArmed = true;

  preload() {
    this.load.spritesheet('robot', 'robot.png', { frameWidth: 32, frameHeight: 32 });
    this.load.spritesheet('egg', 'egg.png', { frameWidth: 32, frameHeight: 32 });
    this.load.spritesheet('bulb', 'bulb.png', { frameWidth: 24, frameHeight: 24 });
    this.load.image('popup', 'popup.png');
  }

  create() {
    const TILE = 32;
    const g = this.add.graphics();
    g.fillStyle(0x6b5d8f, 1).fillRect(0, 0, TILE, TILE);
    g.fillStyle(0x7a6ca0, 1);
    for (let i = -TILE; i < TILE * 2; i += 8) {
      g.fillRect(i, 0, 4, TILE);
    }
    g.lineStyle(1, 0x4a3f6a, 1).strokeRect(0, 0, TILE, TILE);
    g.generateTexture('ground', TILE, TILE);
    g.destroy();
    this.add.tileSprite(0, 0, W, H, 'ground').setOrigin(0, 0);

    DIRS.forEach((dir, row) => {
      this.anims.create({
        key: `robot-walk-${dir}`,
        frames: this.anims.generateFrameNumbers('robot', {
          start: row * 6,
          end: row * 6 + 5,
        }),
        frameRate: 10,
        repeat: -1,
      });
    });

    this.anims.create({
      key: 'egg-wiggle',
      frames: this.anims.generateFrameNumbers('egg', { start: 0, end: 7 }),
      frameRate: 8,
    });
    this.egg = this.physics.add.sprite(W / 2 - 56, H / 2 + 24, 'egg', 0);
    this.egg.setDepth(0);
    const eggBody = this.egg.body as Phaser.Physics.Arcade.Body;
    eggBody.setImmovable(true);
    eggBody.setSize(16, 20).setOffset(8, 6);
    this.egg.on('animationcomplete', () => this.egg.setFrame(0));

    this.robot = this.physics.add.sprite(W / 2, H / 2, 'robot', 0);
    this.robot.setCollideWorldBounds(true);
    this.robot.setDepth(1);
    this.robot.play('robot-walk-S');
    this.robot.anims.pause();
    this.facing = 'S';

    this.physics.add.overlap(this.robot, this.egg, () => {
      if (this.eggArmed) {
        this.eggArmed = false;
        this.egg.play({ key: 'egg-wiggle', repeat: 4 });
      }
      if (this.popupArmed && !this.popupOpen) {
        this.openPopup();
      }
    });

    this.keys = this.input.keyboard!.addKeys({
      up: Phaser.Input.Keyboard.KeyCodes.W,
      down: Phaser.Input.Keyboard.KeyCodes.S,
      left: Phaser.Input.Keyboard.KeyCodes.A,
      right: Phaser.Input.Keyboard.KeyCodes.D,
    }) as Record<'up' | 'down' | 'left' | 'right', Phaser.Input.Keyboard.Key>;
    this.cursors = this.input.keyboard!.createCursorKeys();
    this.confirmKeys = [
      this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE),
      this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.ENTER),
    ];

    // Hover bulb: floats above the egg when bulbOn, glass facing down (flipped).
    this.hoverBulb = this.add.sprite(this.egg.x, this.egg.y - 22, 'bulb', 1);
    this.hoverBulb.setFlipY(true);
    this.hoverBulb.setDepth(2);
    this.hoverBulb.setVisible(false);

    // Popup panel: anchored so notch tip (sprite-local 23,36) sits just above egg.
    this.popup = this.add.image(this.egg.x, this.egg.y - 18, 'popup');
    this.popup.setOrigin(23 / 48, 36 / 40);
    this.popup.setDepth(10);
    this.popup.setVisible(false);

    // Bulb inside popup: focused but unlit (frame 2). Centered on panel body.
    const panelCx = this.popup.x + (24 - 23) * 1; // panel center is 24, notch at 23 → +1
    const panelCy = this.popup.y - 36 + 17;       // panel midpoint vertically (~row 17)
    this.popupBulb = this.add.sprite(panelCx, panelCy, 'bulb', 2);
    this.popupBulb.setDepth(11);
    this.popupBulb.setVisible(false);
  }

  private openPopup() {
    this.popupOpen = true;
    this.popupArmed = false;
    this.popup.setVisible(true);
    this.popupBulb.setVisible(true);
    this.robot.setVelocity(0, 0);
    if (this.robot.anims.isPlaying) {
      this.robot.anims.pause();
      const row = DIRS.indexOf(this.facing);
      this.robot.setFrame(row * 6);
    }
  }

  private closePopup() {
    this.popupOpen = false;
    this.popup.setVisible(false);
    this.popupBulb.setVisible(false);
    this.bulbOn = !this.bulbOn;
    this.hoverBulb.setVisible(this.bulbOn);
  }

  update() {
    if (!this.eggArmed && !this.egg.anims.isPlaying) {
      const overlapping = this.physics.world.overlap(this.robot, this.egg);
      if (!overlapping) this.eggArmed = true;
    }

    if (!this.popupOpen && !this.popupArmed) {
      const overlapping = this.physics.world.overlap(this.robot, this.egg);
      if (!overlapping) this.popupArmed = true;
    }

    if (this.popupOpen) {
      this.robot.setVelocity(0, 0);
      if (this.confirmKeys.some((key) => Phaser.Input.Keyboard.JustDown(key))) {
        this.closePopup();
      }
      return;
    }

    const k = this.keys, c = this.cursors;
    let vx = 0, vy = 0;
    if (k.left.isDown || c.left.isDown) vx -= 1;
    if (k.right.isDown || c.right.isDown) vx += 1;
    if (k.up.isDown || c.up.isDown) vy -= 1;
    if (k.down.isDown || c.down.isDown) vy += 1;

    if (vx !== 0 || vy !== 0) {
      const len = Math.hypot(vx, vy);
      vx = (vx / len) * SPEED;
      vy = (vy / len) * SPEED;
      this.robot.setVelocity(vx, vy);

      const dir = dirFromVelocity(vx, vy);
      if (dir !== this.facing || !this.robot.anims.isPlaying) {
        this.robot.play(`robot-walk-${dir}`, true);
        this.facing = dir;
      }
    } else {
      this.robot.setVelocity(0, 0);
      if (this.robot.anims.isPlaying) {
        this.robot.anims.pause();
        const row = DIRS.indexOf(this.facing);
        this.robot.setFrame(row * 6);
      }
    }
  }
}

new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game',
  width: W,
  height: H,
  pixelArt: true,
  roundPixels: true,
  backgroundColor: '#14171f',
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
    zoom: 2,
  },
  physics: { default: 'arcade', arcade: { debug: false } },
  scene: RobotScene,
});
